"""
Comando para interactuar con la API de BlackboxAI
"""
import click
from rich.console import Console
from api_client import UniversalAPIClient, APIError
from config_extended import get_api_config, get_available_models, get_default_model, AVAILABLE_APIS
from utils import save_conversation_history

console = Console()

@click.command()
@click.argument('mensaje')
@click.option('--modelo', '-m', help='Modelo a utilizar (se mostrará lista si no se especifica)')
@click.option('--guardar/--no-guardar', default=True, help='Guardar conversación en historial')
@click.pass_context
def chat(ctx, mensaje, modelo, guardar):
    """
    Envía un mensaje de texto a la API seleccionada
    
    MENSAJE: El texto que quieres enviar
    """
    api_name = ctx.obj['api']
    config = ctx.obj['config']
    available_models = get_available_models(api_name)
    
    # Validar modelo
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]Error: Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(available_models.keys())}[/yellow]")
        return
    
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    
    try:
        with console.status(f"[bold green]Enviando mensaje a {config['name']}..."):
            messages = [{"role": "user", "content": mensaje}]
            response = client.chat_completions(messages, modelo)
        
        content = client.extract_response_content(response)
        
        console.print(f"[bold blue]Respuesta de {config['name']}:[/bold blue] {content}")
        
        # Guardar en historial
        if guardar:
            conversation = {
                "type": "chat",
                "api": api_name,
                "model": modelo,
                "message": mensaje,
                "response": content
            }
            save_conversation_history(conversation)
            
    except APIError as e:
        console.print(f"[red]Error de {e.api_name}: {e.message}[/red]")
    except Exception as e:
        console.print(f"[red]Error inesperado: {str(e)}[/red]")
