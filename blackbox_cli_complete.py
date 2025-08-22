#!/usr/bin/env python3
"""
CLI para interactuar con múltiples APIs de LLM
"""
import click
import os
import sys
import time
import uuid
from datetime import datetime
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
from logger_config import get_logger, LoggerMixin

console = Console()

class CLILogger(LoggerMixin):
    """Clase para manejar logging específico de la CLI"""
    pass

cli_logger = CLILogger()

def validate_api_key(api_name):
    """Valida que la clave API esté configurada para la API especificada"""
    cli_logger.logger.debug(f"Validating API key for: {api_name}")
    
    config = get_api_config(api_name)
    if not config["api_key"] or config["api_key"] == "your_api_key_here":
        cli_logger.logger.error(
            f"API key not configured for {api_name}",
            extra={'api_name': api_name}
        )
        console.print(f"[red]Error: Clave API no configurada para {config['name']}.[/red]")
        console.print(f"Por favor, configura tu clave API como variable de entorno {AVAILABLE_APIS[api_name]['default_key_env']}")
        sys.exit(1)
    
    cli_logger.logger.debug(f"API key validated successfully for: {api_name}")
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
        cli_logger.logger.debug(f"Creating image message for: {image_path}")
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
        cli_logger.log_error(e, context={'image_path': image_path})
        raise click.ClickException(f"Error procesando imagen: {str(e)}")

def create_pdf_message(text: str, pdf_path: str) -> dict:
    """Crea un mensaje con PDF"""
    try:
        cli_logger.logger.debug(f"Creating PDF message for: {pdf_path}")
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
        cli_logger.log_error(e, context={'pdf_path': pdf_path})
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
    cli_logger.logger.info(f"CLI started with API: {api}")
    
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
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    available_models = get_available_models(api_name)
    
    cli_logger.log_user_action(
        "chat_command_executed",
        request_id=request_id,
        api_name=api_name,
        model_name=modelo,
        message_length=len(mensaje)
    )
    
    # Si no se especifica modelo, usar el por defecto
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        cli_logger.logger.warning(
            f"Invalid model requested: {modelo} for API {api_name}",
            extra={'api_name': api_name, 'model_name': modelo, 'request_id': request_id}
        )
        console.print(f"[red]Error: Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(available_models.keys())}[/yellow]")
        sys.exit(1)
    
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    
    try:
        cli_logger.logger.info(
            f"Sending message to API: {api_name}/{modelo}",
            extra={'request_id': request_id, 'api_name': api_name, 'model_name': modelo}
        )
        
        with console.status(f"[bold green]Enviando mensaje a {config['name']}..."):
            messages = [create_text_message(mensaje)]
            model_name = available_models[modelo]
            
            api_start_time = time.time()
            response = client.chat_completions(messages, model_name)
            api_execution_time = (time.time() - api_start_time) * 1000
        
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
        
        # Log de la llamada a la API
        cli_logger.log_api_call(
            api_name=api_name,
            model_name=modelo,
            execution_time=api_execution_time,
            tokens_used=usage.get('total_tokens') if usage else None,
            request_id=request_id
        )
        
        # Guardar en historial
        if guardar:
            conversation = {
                "type": "chat",
                "api": api_name,
                "model": modelo,
                "message": mensaje,
                "response": content,
                "usage": usage,
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            }
            save_conversation_history(conversation)
        
        total_execution_time = (time.time() - start_time) * 1000
        cli_logger.logger.info(
            f"Chat command completed successfully",
            extra={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': modelo,
                'execution_time': total_execution_time,
                'tokens_used': usage.get('total_tokens') if usage else None,
                'response_length': len(content)
            }
        )
            
    except APIError as e:
        cli_logger.log_error(
            e,
            context={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': modelo,
                'error_type': 'api_error'
            },
            error_code=f"API_{e.status_code}"
        )
        console.print(f"[red]Error de {e.api_name}: {e.message}[/red]")
        if e.status_code:
            console.print(f"[red]Código de estado: {e.status_code}[/red]")
        sys.exit(1)
    except Exception as e:
        cli_logger.log_error(
            e,
            context={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': modelo,
                'error_type': 'unexpected_error'
            }
        )
        console.print(f"[red]Error inesperado: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--limite', '-l', default=10, help='Número de conversaciones a mostrar')
def historial(limite):
    """
    Muestra el historial de conversaciones
    """
    cli_logger.logger.info(f"Fetching history with limit: {limite}")
    
    history = load_conversation_history()
    
    if not history:
        console.print("[yellow]No hay conversaciones en el historial[/yellow]")
        cli_logger.logger.info("No conversations found in history")
        return
    
    # Mostrar las últimas conversaciones
    recent_conversations = history[-limite:]
    
    table = Table(title="Historial de Conversaciones")
    table.add_column("Fecha", style="cyan")
    table.add_column("Tipo", style="magenta")
    table.add_column("API", style="blue")
    table.add_column("Modelo", style="green")
    table.add_column("Mensaje/Archivo", style="white")
    table.add_column("Tokens", style="yellow")
    
    for conv in recent_conversations:
        timestamp = conv.get("timestamp", "N/A")
        if timestamp != "N/A":
            # Formatear fecha
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        conv_type = conv.get("type", "N/A")
        api_name = conv.get("api", "N/A")
        model = conv.get("model", "N/A")
        
        # Obtener mensaje o archivo
        if conv_type in ["chat", "interactive", "web_chat"]:
            content = conv.get("message", "N/A")[:50] + "..." if len(conv.get("message", "")) > 50 else conv.get("message", "N/A")
        else:
            content = conv.get("file", "N/A")
        
        tokens = str(conv.get("usage", {}).get("total_tokens", "N/A")) if conv.get("usage") else "N/A"
        
        table.add_row(timestamp, conv_type, api_name, model, content, tokens)
    
    console.print(table)
    
    cli_logger.logger.info(f"History displayed: {len(recent_conversations)} conversations")

@cli.command()
@click.pass_context
def modelos(ctx):
    """
    Lista los modelos disponibles para la API seleccionada
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    available_models = get_available_models(api_name)
    
    cli_logger.logger.info(f"Listing models for API: {api_name}")
    
    table = Table(title=f"Modelos Disponibles para {config['name']}")
    table.add_column("Nombre", style="cyan")
    table.add_column("ID del Modelo", style="green")
    table.add_column("Descripción", style="white")
    
    descriptions = {
        "gpt-4": "Modelo GPT-4 estándar para texto",
        "gpt-4o": "GPT-4o - Optimizado y más rápido",
        "gpt-4o-mini": "GPT-4o Mini - Versión ligera",
        "gpt-4-turbo": "GPT-4 Turbo - Más rápido y actualizado",
        "gpt-3.5-turbo": "Modelo más rápido y económico",
        "gpt-3.5-turbo-16k": "GPT-3.5 con contexto extendido",
        "claude-3.5-sonnet": "Claude 3.5 Sonnet - Última versión mejorada",
        "claude-3.5-haiku": "Claude 3.5 Haiku - Rápido y eficiente",
        "claude-3-opus": "Claude 3 Opus - El más potente de Anthropic",
        "claude-3-sonnet": "Claude 3 Sonnet - Equilibrio entre velocidad y capacidad",
        "claude-3-haiku": "Claude 3 Haiku - El más rápido de Anthropic",
        "claude-2.1": "Claude 2.1 - Versión mejorada",
        "claude-2": "Claude 2.0 - Modelo base de Anthropic",
        "llama-3.1-405b": "Llama 3.1 405B - Modelo masivo de Meta",
        "llama-3.1-70b": "Llama 3.1 70B - Modelo grande de Meta",
        "llama-3.1-8b": "Llama 3.1 8B - Modelo rápido de Meta",
        "llama-3.3-70b": "Llama 3.3 70B - Versión actualizada",
        "mixtral-8x7b": "Mixtral 8x7B - Modelo de mezcla de expertos",
        "mixtral-8x22b": "Mixtral 8x22B - Versión más grande",
        "mistral-large": "Mistral Large - Modelo principal de Mistral",
        "gemini-2.5-flash": "Gemini 2.5 Flash - Última versión de Google",
        "gemini-2.0-flash": "Gemini 2.0 Flash - Versión rápida",
        "gemini-flash-1.5": "Gemini Flash 1.5 - Modelo eficiente",
        "deepseek-r1": "DeepSeek R1 - Modelo de razonamiento",
        "deepseek-chat": "DeepSeek Chat - Modelo conversacional",
        "qwen-max": "Qwen Max - Modelo principal de Alibaba",
        "qwen-2.5-72b": "Qwen 2.5 72B - Versión grande",
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
    
    cli_logger.logger.info(
        f"Models listed for {api_name}: {len(available_models)} models available",
        extra={'api_name': api_name, 'model_count': len(available_models), 'default_model': default_model}
    )

if __name__ == "__main__":
    try:
        cli_logger.logger.info("CLI application starting")
        cli()
    except Exception as e:
        cli_logger.log_error(e, context={'component': 'cli_startup'})
        raise
    finally:
        cli_logger.logger.info("CLI application finished")
