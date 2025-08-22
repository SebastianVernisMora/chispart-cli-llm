#!/usr/bin/env python3
"""
CLI para interactuar con la API de BlackboxAI
"""
import click
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown

from api_client import UniversalAPIClient, APIError
from config import (
    get_api_config, get_available_models, get_default_model, 
    AVAILABLE_APIS, DEFAULT_API, VISION_SUPPORTED_APIS, PDF_SUPPORTED_APIS
)
from utils import (
    is_supported_image, is_supported_pdf, create_image_data_url, 
    create_pdf_data_url, save_conversation_history, load_conversation_history,
    format_file_size, validate_file_size
)

console = Console()


def validate_api_key(api_name):
    """Valida que la clave API esté configurada para la API especificada"""
    config = get_api_config(api_name)
    if not config["api_key"] or config["api_key"] == "your_api_key_here":
        console.print(f"[red]Error: Clave API no configurada para {config['name']}.[/red]")
        console.print(f"Por favor, configura tu clave API como variable de entorno {AVAILABLE_APIS[api_name]['default_key_env']}")
        sys.exit(1)
    return config


def create_text_message(content: str) -> dict:
    """Crea un mensaje de texto"""
    return {
        "role": "user",
        "content": content
    }


def create_image_message(text: str, image_path: str) -> dict:
    """Crea un mensaje con imagen"""
    try:
        image_url = create_image_data_url(image_path)
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    except Exception as e:
        raise click.ClickException(f"Error procesando imagen: {str(e)}")


def create_pdf_message(text: str, pdf_path: str) -> dict:
    """Crea un mensaje con PDF"""
    try:
        pdf_url = create_pdf_data_url(pdf_path)
        filename = os.path.basename(pdf_path)
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                },
                {
                    "type": "file",
                    "file": {
                        "filename": filename,
                        "file_data": pdf_url
                    }
                }
            ]
        }
    except Exception as e:
        raise click.ClickException(f"Error procesando PDF: {str(e)}")


@click.group()
@click.option('--api', '-a', default=DEFAULT_API, 
              type=click.Choice(list(AVAILABLE_APIS.keys())), 
              help='API a utilizar')
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx, api):
    """
    🤖 CLI Universal para LLMs
    
    Una herramienta de línea de comandos para enviar mensajes, imágenes y PDFs a múltiples APIs de LLM.
    """
    # Asegurar que el contexto existe
    ctx.ensure_object(dict)
    ctx.obj['api'] = api
    
    # Validar API key para la API seleccionada
    config = validate_api_key(api)
    ctx.obj['config'] = config


@cli.command()
@click.argument('mensaje')
@click.option('--modelo', '-m', help='Modelo a utilizar (se mostrará lista si no se especifica)')
@click.option('--guardar/--no-guardar', default=True, 
              help='Guardar conversación en historial')
@click.pass_context
def chat(ctx, mensaje, modelo, guardar):
    """
    Envía un mensaje de texto a la API seleccionada
    
    MENSAJE: El texto que quieres enviar
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    available_models = get_available_models(api_name)
    
    # Si no se especifica modelo, usar el por defecto
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]Error: Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(available_models.keys())}[/yellow]")
        sys.exit(1)
    
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    
    try:
        with console.status(f"[bold green]Enviando mensaje a {config['name']}..."):
            messages = [create_text_message(mensaje)]
            model_name = available_models[modelo]
            response = client.chat_completions(messages, model_name)
        
        # Mostrar respuesta
        content = client.extract_response_content(response)
        
        console.print(Panel(
            Markdown(content),
            title=f"[bold blue]Respuesta de {config['name']}[/bold blue]",
            border_style="blue"
        ))
        
        # Mostrar información de uso si está disponible
        usage = client.get_usage_info(response)
        if usage:
            console.print(f"\n[dim]Tokens utilizados: {usage.get('total_tokens', 'N/A')}[/dim]")
        
        # Guardar en historial
        if guardar:
            conversation = {
                "type": "chat",
                "api": api_name,
                "model": modelo,
                "message": mensaje,
                "response": content,
                "usage": usage
            }
            save_conversation_history(conversation)
            
    except APIError as e:
        console.print(f"[red]Error de {e.api_name}: {e.message}[/red]")
        if e.status_code:
            console.print(f"[red]Código de estado: {e.status_code}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error inesperado: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('archivo')
@click.option('--prompt', '-p', default="¿Qué hay en esta imagen?", 
              help='Pregunta sobre la imagen')
@click.option('--modelo', '-m', help='Modelo a utilizar (se mostrará lista si no se especifica)')
@click.option('--guardar/--no-guardar', default=True, 
              help='Guardar conversación en historial')
@click.pass_context
def imagen(ctx, archivo, prompt, modelo, guardar):
    """
    Analiza una imagen con la API seleccionada
    
    ARCHIVO: Ruta de la imagen a analizar
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    
    # Verificar si la API soporta imágenes
    if api_name not in VISION_SUPPORTED_APIS:
        console.print(f"[red]Error: {config['name']} no soporta análisis de imágenes[/red]")
        console.print(f"[yellow]APIs que soportan imágenes: {', '.join(VISION_SUPPORTED_APIS)}[/yellow]")
        sys.exit(1)
    
    available_models = get_available_models(api_name)
    
    # Si no se especifica modelo, usar gpt-4-vision si está disponible, sino el por defecto
    if not modelo:
        if "gpt-4-vision" in available_models:
            modelo = "gpt-4-vision"
        else:
            modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]Error: Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(available_models.keys())}[/yellow]")
        sys.exit(1)
    
    # Validaciones
    if not os.path.exists(archivo):
        raise click.ClickException(f"El archivo {archivo} no existe")
    
    if not is_supported_image(archivo):
        raise click.ClickException(f"Formato de imagen no soportado. Usa: jpg, jpeg, png, webp")
    
    if not validate_file_size(archivo, 20):
        file_size = format_file_size(os.path.getsize(archivo))
        raise click.ClickException(f"El archivo es demasiado grande ({file_size}). Máximo: 20MB")
    
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    
    try:
        with console.status(f"[bold green]Analizando imagen con {config['name']}..."):
            messages = [create_image_message(prompt, archivo)]
            model_name = available_models[modelo]
            response = client.chat_completions(messages, model_name)
        
        # Mostrar respuesta
        content = client.extract_response_content(response)
        
        console.print(Panel(
            Markdown(content),
            title=f"[bold blue]Análisis de {os.path.basename(archivo)} - {config['name']}[/bold blue]",
            border_style="blue"
        ))
        
        # Mostrar información de uso
        usage = client.get_usage_info(response)
        if usage:
            console.print(f"\n[dim]Tokens utilizados: {usage.get('total_tokens', 'N/A')}[/dim]")
        
        # Guardar en historial
        if guardar:
            conversation = {
                "type": "image",
                "api": api_name,
                "model": modelo,
                "file": archivo,
                "prompt": prompt,
                "response": content,
                "usage": usage
            }
            save_conversation_history(conversation)
            
    except APIError as e:
        console.print(f"[red]Error de {e.api_name}: {e.message}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error inesperado: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('archivo')
@click.option('--prompt', '-p', default="Resume el contenido de este documento", 
              help='Pregunta sobre el PDF')
@click.option('--modelo', '-m', help='Modelo a utilizar (se mostrará lista si no se especifica)')
@click.option('--guardar/--no-guardar', default=True, 
              help='Guardar conversación en historial')
@click.pass_context
def pdf(ctx, archivo, prompt, modelo, guardar):
    """
    Analiza un documento PDF con la API seleccionada
    
    ARCHIVO: Ruta del PDF a analizar
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    
    # Verificar si la API soporta PDFs
    if api_name not in PDF_SUPPORTED_APIS:
        console.print(f"[red]Error: {config['name']} no soporta análisis de PDFs[/red]")
        console.print(f"[yellow]APIs que soportan PDFs: {', '.join(PDF_SUPPORTED_APIS)}[/yellow]")
        sys.exit(1)
    
    available_models = get_available_models(api_name)
    
    # Si no se especifica modelo, usar el por defecto
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]Error: Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(available_models.keys())}[/yellow]")
        sys.exit(1)
    
    # Validaciones
    if not os.path.exists(archivo):
        raise click.ClickException(f"El archivo {archivo} no existe")
    
    if not is_supported_pdf(archivo):
        raise click.ClickException(f"El archivo debe ser un PDF")
    
    if not validate_file_size(archivo, 20):
        file_size = format_file_size(os.path.getsize(archivo))
        raise click.ClickException(f"El archivo es demasiado grande ({file_size}). Máximo: 20MB")
    
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    
    try:
        with console.status(f"[bold green]Procesando PDF con {config['name']}..."):
            messages = [create_pdf_message(prompt, archivo)]
            model_name = available_models[modelo]
            response = client.chat_completions(messages, model_name)
        
        # Mostrar respuesta
        content = client.extract_response_content(response)
        
        console.print(Panel(
            Markdown(content),
            title=f"[bold blue]Análisis de {os.path.basename(archivo)} - {config['name']}[/bold blue]",
            border_style="blue"
        ))
        
        # Mostrar información de uso
        usage = client.get_usage_info(response)
        if usage:
            console.print(f"\n[dim]Tokens utilizados: {usage.get('total_tokens', 'N/A')}[/dim]")
        
        # Guardar en historial
        if guardar:
            conversation = {
                "type": "pdf",
                "api": api_name,
                "model": modelo,
                "file": archivo,
                "prompt": prompt,
                "response": content,
                "usage": usage
            }
            save_conversation_history(conversation)
            
    except APIError as e:
        console.print(f"[red]Error de {e.api_name}: {e.message}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error inesperado: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--modelo', '-m', help='Modelo a utilizar (se mostrará lista si no se especifica)')
@click.pass_context
def interactivo(ctx, modelo):
    """
    Inicia una sesión de chat interactiva
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    available_models = get_available_models(api_name)
    
    # Si no se especifica modelo, usar el por defecto
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]Error: Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(available_models.keys())}[/yellow]")
        sys.exit(1)
    
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    messages = []
    
    console.print(Panel(
        f"[bold green]🤖 Sesión interactiva con {config['name']}[/bold green]\n"
        "Escribe 'salir', 'exit' o 'quit' para terminar\n"
        "Escribe 'limpiar' o 'clear' para limpiar el historial de la sesión",
        title="Modo Interactivo",
        border_style="green"
    ))
    
    console.print(f"[dim]API: {config['name']} | Modelo: {modelo}[/dim]\n")
    
    while True:
        try:
            # Obtener input del usuario
            user_input = Prompt.ask("[bold cyan]Tú")
            
            # Comandos especiales
            if user_input.lower() in ['salir', 'exit', 'quit']:
                console.print("[yellow]¡Hasta luego![/yellow]")
                break
            elif user_input.lower() in ['limpiar', 'clear']:
                messages = []
                console.print("[yellow]Historial de sesión limpiado[/yellow]")
                continue
            elif not user_input.strip():
                continue
            
            # Agregar mensaje del usuario
            messages.append(create_text_message(user_input))
            
            # Enviar a la API
            with console.status(f"[bold green]Pensando con {config['name']}..."):
                model_name = available_models[modelo]
                response = client.chat_completions(messages, model_name)
            
            # Obtener y mostrar respuesta
            content = client.extract_response_content(response)
            
            console.print(f"[bold blue]{config['name']}:[/bold blue] {content}\n")
            
            # Agregar respuesta al historial de la sesión
            messages.append({
                "role": "assistant",
                "content": content
            })
            
            # Guardar conversación
            conversation = {
                "type": "interactive",
                "api": api_name,
                "model": modelo,
                "message": user_input,
                "response": content,
                "usage": client.get_usage_info(response)
            }
            save_conversation_history(conversation)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Sesión interrumpida. ¡Hasta luego![/yellow]")
            break
        except APIError as e:
            console.print(f"[red]Error de {e.api_name}: {e.message}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.option('--limite', '-l', default=10, help='Número de conversaciones a mostrar')
def historial(limite):
    """
    Muestra el historial de conversaciones
    """
    history = load_conversation_history()
    
    if not history:
        console.print("[yellow]No hay conversaciones en el historial[/yellow]")
        return
    
    # Mostrar las últimas conversaciones
    recent_conversations = history[-limite:]
    
    table = Table(title="Historial de Conversaciones")
    table.add_column("Fecha", style="cyan")
    table.add_column("Tipo", style="magenta")
    table.add_column("Modelo", style="green")
    table.add_column("Mensaje/Archivo", style="white")
    table.add_column("Tokens", style="yellow")
    
    for conv in recent_conversations:
        timestamp = conv.get("timestamp", "N/A")
        if timestamp != "N/A":
            # Formatear fecha
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp)
            timestamp = dt.strftime("%Y-%m-%d %H:%M")
        
        conv_type = conv.get("type", "N/A")
        model = conv.get("model", "N/A")
        
        # Obtener mensaje o archivo
        if conv_type == "chat":
            content = conv.get("message", "N/A")[:50] + "..." if len(conv.get("message", "")) > 50 else conv.get("message", "N/A")
        else:
            content = conv.get("file", "N/A")
        
        tokens = str(conv.get("usage", {}).get("total_tokens", "N/A")) if conv.get("usage") else "N/A"
        
        table.add_row(timestamp, conv_type, model, content, tokens)
    
    console.print(table)


@cli.command()
@click.pass_context
def modelos(ctx):
    """
    Lista los modelos disponibles para la API seleccionada
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    available_models = get_available_models(api_name)
    
    table = Table(title=f"Modelos Disponibles para {config['name']}")
    table.add_column("Nombre", style="cyan")
    table.add_column("ID del Modelo", style="green")
    table.add_column("Descripción", style="white")
    
    descriptions = {
        "gpt-4": "Modelo GPT-4 estándar para texto",
        "gpt-4-vision": "GPT-4 con capacidades de visión para imágenes",
        "gpt-4-turbo": "GPT-4 Turbo - Más rápido y actualizado",
        "gpt-3.5-turbo": "Modelo más rápido y económico",
        "gpt-3.5-turbo-16k": "GPT-3.5 con contexto extendido",
        "claude-3-opus": "Claude 3 Opus - El más potente de Anthropic",
        "claude-3-sonnet": "Claude 3 Sonnet - Equilibrio entre velocidad y capacidad",
        "claude-3-haiku": "Claude 3 Haiku - El más rápido de Anthropic",
        "claude-2.1": "Claude 2.1 - Versión mejorada",
        "claude-2": "Claude 2.0 - Modelo base de Anthropic",
        "llama-3.1-70b": "Llama 3.1 70B - Modelo grande de Meta",
        "llama-3.1-8b": "Llama 3.1 8B - Modelo rápido de Meta",
        "mixtral-8x7b": "Mixtral 8x7B - Modelo de mezcla de expertos",
        "gemini-pro": "Gemini Pro - Modelo avanzado de Google",
        "gemma-7b": "Gemma 7B - Modelo abierto de Google",
        "qwen-2-72b": "Qwen 2 72B - Modelo de Alibaba"
    }
    
    for name, model_id in available_models.items():
        description = descriptions.get(name, f"Modelo de {config['name']}")
        table.add_row(name, model_id, description)
    
    console.print(table)
    
    # Mostrar modelo por defecto
    default_model = get_default_model(api_name)
    console.print(f"\n[dim]Modelo por defecto: {default_model}[/dim]")


if __name__ == "__main__":
    cli()
