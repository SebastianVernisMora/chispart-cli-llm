#!/usr/bin/env python3
"""
Chispart Dev Agent - CLI Avanzada para Desarrollo
Incluye perfiles de desarrollo, split chat, seguridad y más modelos
"""

import click
import os
import sys
import webbrowser
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.markdown import Markdown

# Importar módulos del sistema
from config_extended import (
    get_api_config, get_available_models, get_default_model,
    AVAILABLE_APIS, DEFAULT_API, VISION_SUPPORTED_APIS, PDF_SUPPORTED_APIS
)
from api_client import UniversalAPIClient, APIError
from utils import (
    is_supported_image, is_supported_pdf, create_image_data_url,
    extract_text_from_pdf, save_conversation_history, load_conversation_history,
    format_file_size, validate_file_size
)

# Importar nuevos módulos
from core.dev_profiles import profile_manager, DevProfile
from core.split_chat_manager import split_chat_manager
from core.security_manager import security_manager
from core.theme_manager import theme_manager
from core.conversation_manager import conversation_manager
from core.team_manager import team_manager
from core.atc_agent import atc_agent

console = Console()

def validate_api_key(api_name):
    """Valida que la clave API esté configurada"""
    config = get_api_config(api_name)
    if not config["api_key"] or config["api_key"] == "your_api_key_here":
        console.print(f"[red]Error: Clave API no configurada para {config['name']}.[/red]")
        console.print(f"Configura tu clave API: export BLACKBOX_API_KEY='tu_clave'")
        sys.exit(1)
    return config

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--debug', is_flag=True, help='Activar modo debug')
@click.option('--theme', type=click.Choice(['neon', 'dark', 'light', 'retro']), 
              help='Tema de la interfaz')
@click.option('--profile', type=click.Choice(['devops', 'frontend', 'backend', 'fullstack', 'educator', 'qa', 'project_leader']),
              help='Perfil de desarrollo a usar')
@click.version_option(version="2.1.0")
@click.pass_context
def cli(ctx, debug, theme, profile):
    """
    🚀 Chispart Dev Agent - Asistente IA para Desarrollo
    
    Una herramienta avanzada para desarrolladores con perfiles especializados,
    split chat, seguridad mejorada y acceso a 60+ modelos de IA.
    
    \b
    Características principales:
    • 7 Perfiles de desarrollo especializados
    • Sistema de split/merge chat
    • Seguridad con whitelist de comandos
    • 60+ modelos de IA potentes
    • Interfaz moderna y optimizada
    
    Ejemplos de uso:
      chispart-dev chat "Crea una API REST con FastAPI" --profile backend
      chispart-dev split-chat "Frontend Team" --profile frontend
      chispart-dev merge-chat session1 session2 --name "Full Stack Review"
      chispart-dev execute "git status" --safe
    """
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    
    # Configurar tema si se especifica
    if theme:
        theme_manager.set_theme(theme)
    
    # Configurar perfil si se especifica
    if profile:
        profile_manager.set_current_profile(profile)
        console.print(f"✅ Perfil activado: [bold cyan]{profile}[/bold cyan]")
    
    # Validar API key para comandos que lo requieren
    if ctx.invoked_subcommand not in ['perfiles', 'split-list', 'security', 'help']:
        config = validate_api_key('chispart')
        ctx.obj['config'] = config

@cli.command()
@click.argument('mensaje')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--profile', type=click.Choice(['devops', 'frontend', 'backend', 'fullstack', 'educator', 'qa', 'project_leader']),
              help='Perfil de desarrollo para este chat')
@click.option('--no-guardar', is_flag=True, help='No guardar en historial')
@click.pass_context
def chat(ctx, mensaje: str, modelo: Optional[str], profile: Optional[str], no_guardar: bool):
    """
    💬 Chat con IA usando perfiles de desarrollo
    
    Envía mensajes optimizados según el perfil de desarrollo seleccionado.
    
    Ejemplos:
      chispart-dev chat "Crea un componente React" --profile frontend
      chispart-dev chat "Diseña una arquitectura de microservicios" --profile devops
      chispart-dev chat "Explica async/await en Python" --profile educator
    """
    config = ctx.obj['config']
    
    # Configurar perfil temporal si se especifica
    original_profile = profile_manager.get_current_profile()
    if profile:
        profile_manager.set_current_profile(profile)
    
    try:
        # Obtener modelos disponibles
        available_models = get_available_models('chispart')
        
        # Seleccionar modelo
        if not modelo:
            current_profile = profile_manager.get_current_profile()
            if current_profile and current_profile.preferred_models:
                modelo = current_profile.preferred_models[0]
            else:
                modelo = get_default_model('chispart')
        elif modelo not in available_models:
            console.print(f"[red]Error: Modelo '{modelo}' no disponible[/red]")
            console.print(f"[yellow]Modelos disponibles: {', '.join(list(available_models.keys())[:10])}...[/yellow]")
            sys.exit(1)
        
        # Crear cliente API
        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        
        # Preparar mensajes
        messages = []
        
        # Añadir system prompt del perfil si existe
        current_profile = profile_manager.get_current_profile()
        if current_profile:
            messages.append({
                "role": "system",
                "content": current_profile.system_prompt
            })
            console.print(f"📋 Usando perfil: [bold cyan]{current_profile.name}[/bold cyan]")
        
        # Añadir mensaje del usuario
        messages.append({
            "role": "user",
            "content": mensaje
        })
        
        # Mostrar información del chat
        console.print(Panel(
            f"[bold]API:[/bold] {config['name']}\n"
            f"[bold]Modelo:[/bold] {modelo}\n"
            f"[bold]Perfil:[/bold] {current_profile.name if current_profile else 'Ninguno'}\n"
            f"[bold]Mensaje:[/bold] {mensaje[:100]}{'...' if len(mensaje) > 100 else ''}",
            title="📤 Chat",
            border_style="cyan"
        ))
        
        # Enviar a la API
        with console.status(f"[bold green]Enviando mensaje a {config['name']}..."):
            model_name = available_models[modelo]
            response = client.chat_completions(messages, model_name)
        
        # Mostrar respuesta
        content = client.extract_response_content(response)
        
        console.print(Panel(
            Markdown(content),
            title=f"[bold blue]Respuesta - {config['name']}[/bold blue]",
            border_style="blue"
        ))
        
        # Mostrar información de uso
        usage = client.get_usage_info(response)
        if usage:
            console.print(f"⏱️ Tokens: {usage.get('total_tokens', 'N/A')} | Modelo: {modelo}")
        
        # Guardar en historial
        if not no_guardar:
            conversation = {
                "type": "dev_chat",
                "profile": current_profile.name if current_profile else None,
                "model": modelo,
                "message": mensaje,
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
    finally:
        # Restaurar perfil original
        if profile and original_profile:
            profile_manager.set_current_profile(original_profile.name)

@cli.command()
def perfiles():
    """
    👥 Gestiona perfiles de desarrollo
    
    Lista y configura perfiles especializados para diferentes roles de desarrollo.
    """
    profiles = profile_manager.list_profiles()
    current = profile_manager.get_current_profile()
    
    table = Table(title="Perfiles de Desarrollo Disponibles")
    table.add_column("Perfil", style="cyan")
    table.add_column("Descripción", style="white")
    table.add_column("Estado", style="green")
    table.add_column("Modelos Preferidos", style="yellow")
    
    for name, description in profiles.items():
        profile = profile_manager.get_profile(name)
        status = "🌟 Activo" if current and current.name.lower() == name else ""
        preferred = ", ".join(profile.preferred_models[:3]) if profile else ""
        table.add_row(name.title(), description, status, preferred)
    
    console.print(table)
    
    # Opción para cambiar perfil
    if Confirm.ask("\n¿Quieres cambiar el perfil activo?"):
        profile_choices = list(profiles.keys())
        profile_name = Prompt.ask(
            "Selecciona un perfil",
            choices=profile_choices,
            default=current.name.lower() if current else profile_choices[0]
        )
        
        if profile_manager.set_current_profile(profile_name):
            console.print(f"✅ Perfil cambiado a: [bold cyan]{profile_name.title()}[/bold cyan]")
            
            # Mostrar prompts de ejemplo
            examples = profile_manager.get_example_prompts(profile_name)
            if examples:
                console.print("\n📝 Prompts de ejemplo para este perfil:")
                for i, example in enumerate(examples[:3], 1):
                    console.print(f"  {i}. {example}")
        else:
            console.print("[red]Error cambiando perfil[/red]")

@cli.command()
@click.argument('name')
@click.option('--profile', type=click.Choice(['devops', 'frontend', 'backend', 'fullstack', 'educator', 'qa', 'project_leader']),
              help='Perfil de desarrollo para la sesión')
@click.option('--modelo', '-m', help='Modelo específico para la sesión')
def split_chat(name: str, profile: Optional[str], modelo: Optional[str]):
    """
    🔀 Crea una nueva sesión de split chat
    
    Inicia una sesión de chat paralela con su propio servidor web.
    
    Ejemplos:
      chispart-dev split-chat "Frontend Team" --profile frontend
      chispart-dev split-chat "Backend API" --profile backend --modelo deepseek-coder
    """
    console.print(f"🚀 Creando split chat: [bold cyan]{name}[/bold cyan]")
    
    session = split_chat_manager.create_split_chat(name, profile, modelo)
    
    if session:
        console.print(Panel(
            f"[bold green]✅ Split chat creado exitosamente[/bold green]\n\n"
            f"[bold]ID de Sesión:[/bold] {session.id}\n"
            f"[bold]Nombre:[/bold] {session.name}\n"
            f"[bold]Puerto:[/bold] {session.port}\n"
            f"[bold]Perfil:[/bold] {session.profile or 'Ninguno'}\n"
            f"[bold]Modelo:[/bold] {session.model or 'Por defecto'}\n\n"
            f"[bold cyan]🌐 Accede en:[/bold cyan] http://localhost:{session.port}\n"
            f"[bold yellow]💡 Tip:[/bold yellow] Usa 'chispart-dev split-list' para ver todas las sesiones",
            title="Split Chat Creado",
            border_style="green"
        ))
        
        # Abrir en navegador si es posible
        if Confirm.ask("¿Abrir en el navegador?", default=True):
            try:
                webbrowser.open(f"http://localhost:{session.port}")
            except Exception:
                console.print("[yellow]No se pudo abrir el navegador automáticamente[/yellow]")
    else:
        console.print("[red]❌ Error creando split chat. Máximo de sesiones alcanzado o puerto no disponible.[/red]")

@cli.command()
def split_list():
    """
    📋 Lista todas las sesiones de split chat
    
    Muestra el estado de todas las sesiones activas y detenidas.
    """
    sessions = split_chat_manager.list_sessions()
    
    if not sessions:
        console.print("[yellow]No hay sesiones de split chat activas[/yellow]")
        return
    
    table = Table(title="Sesiones de Split Chat")
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="white")
    table.add_column("Puerto", style="green")
    table.add_column("Estado", style="yellow")
    table.add_column("Perfil", style="magenta")
    table.add_column("Modelo", style="blue")
    table.add_column("Creada", style="dim")
    
    for session in sessions:
        status_icon = "🟢" if session.status == "active" else "🔴"
        status = f"{status_icon} {session.status.title()}"
        
        table.add_row(
            session.id,
            session.name,
            str(session.port),
            status,
            session.profile or "-",
            session.model or "default",
            session.created_at[:16]
        )
    
    console.print(table)
    
    # Opciones de gestión
    console.print("\n[bold]Opciones:[/bold]")
    console.print("• Para detener una sesión: [cyan]chispart-dev split-stop <session_id>[/cyan]")
    console.print("• Para fusionar sesiones: [cyan]chispart-dev merge-chat <id1> <id2>[/cyan]")

@cli.command()
@click.argument('session_id')
def split_stop(session_id: str):
    """
    🛑 Detiene una sesión de split chat
    
    Termina una sesión específica y libera su puerto.
    """
    if split_chat_manager.stop_split_chat(session_id):
        console.print(f"✅ Sesión [cyan]{session_id}[/cyan] detenida correctamente")
    else:
        console.print(f"[red]❌ Error deteniendo sesión {session_id}[/red]")

@cli.command()
@click.argument('session_ids', nargs=-1, required=True)
@click.option('--name', default="Merged Chat", help='Nombre para el chat fusionado')
def merge_chat(session_ids, name: str):
    """
    🔗 Fusiona múltiples sesiones de split chat
    
    Combina el contexto de varias sesiones en una nueva sesión.
    
    Ejemplo:
      chispart-dev merge-chat abc123 def456 --name "Full Stack Review"
    """
    if len(session_ids) < 2:
        console.print("[red]❌ Necesitas al menos 2 sesiones para fusionar[/red]")
        return
    
    console.print(f"🔗 Fusionando {len(session_ids)} sesiones en: [bold cyan]{name}[/bold cyan]")
    
    merged_id = split_chat_manager.merge_chats(list(session_ids), name)
    
    if merged_id:
        merged_session = split_chat_manager.get_session(merged_id)
        console.print(Panel(
            f"[bold green]✅ Sesiones fusionadas exitosamente[/bold green]\n\n"
            f"[bold]Nueva Sesión ID:[/bold] {merged_id}\n"
            f"[bold]Nombre:[/bold] {name}\n"
            f"[bold]Puerto:[/bold] {merged_session.port}\n"
            f"[bold]Sesiones Originales:[/bold] {', '.join(session_ids)}\n\n"
            f"[bold cyan]🌐 Accede en:[/bold cyan] http://localhost:{merged_session.port}",
            title="Chat Fusionado",
            border_style="green"
        ))
    else:
        console.print("[red]❌ Error fusionando sesiones[/red]")

@cli.command()
@click.argument('command')
@click.option('--safe', is_flag=True, help='Ejecutar con validación de seguridad')
@click.option('--confirm', is_flag=True, help='Pedir confirmación antes de ejecutar')
def execute(command: str, safe: bool, confirm: bool):
    """
    ⚡ Ejecuta comandos del sistema con seguridad
    
    Ejecuta comandos validados por el sistema de seguridad.
    
    Ejemplos:
      chispart-dev execute "git status" --safe
      chispart-dev execute "npm install" --safe --confirm
    """
    if safe:
        validation = security_manager.validate_command(command)
        
        if not validation.is_allowed:
            console.print(f"[red]❌ Comando no permitido: {validation.reason}[/red]")
            if validation.suggested_alternative:
                console.print(f"[yellow]💡 Sugerencia: {validation.suggested_alternative}[/yellow]")
            return
        
        if validation.requires_confirmation or confirm:
            if not Confirm.ask(f"¿Ejecutar comando: [cyan]{command}[/cyan]?"):
                console.print("[yellow]Comando cancelado[/yellow]")
                return
    
    console.print(f"⚡ Ejecutando: [cyan]{command}[/cyan]")
    
    if safe:
        success, stdout, stderr = security_manager.execute_safe_command(command)
    else:
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired:
            success = False
            stdout = ""
            stderr = "Comando excedió el tiempo límite"
        except Exception as e:
            success = False
            stdout = ""
            stderr = str(e)
    
    if success:
        if stdout:
            console.print(Panel(stdout, title="📤 Salida", border_style="green"))
        console.print("[green]✅ Comando ejecutado exitosamente[/green]")
    else:
        if stderr:
            console.print(Panel(stderr, title="❌ Error", border_style="red"))
        console.print("[red]❌ Error ejecutando comando[/red]")

@cli.command()
def security():
    """
    🛡️ Gestiona la configuración de seguridad
    
    Muestra y configura el sistema de seguridad con whitelist.
    """
    status = security_manager.get_security_status()
    
    console.print(Panel(
        f"[bold]Estado:[/bold] {'🟢 Habilitado' if status['enabled'] else '🔴 Deshabilitado'}\n"
        f"[bold]Comandos Permitidos:[/bold] {status['whitelist_count']}\n"
        f"[bold]Comandos Bloqueados:[/bold] {status['blacklist_count']}\n"
        f"[bold]Requieren Confirmación:[/bold] {status['confirmation_required_count']}",
        title="🛡️ Estado de Seguridad",
        border_style="blue"
    ))
    
    # Mostrar algunos comandos de cada categoría
    console.print("\n[bold green]✅ Comandos Permitidos (algunos):[/bold green]")
    for cmd in status['whitelist'][:10]:
        console.print(f"  • {cmd}")
    
    console.print("\n[bold red]❌ Comandos Bloqueados (algunos):[/bold red]")
    for cmd in status['blacklist'][:10]:
        console.print(f"  • {cmd}")
    
    # Opciones de configuración
    if Confirm.ask("\n¿Quieres modificar la configuración de seguridad?"):
        action = Prompt.ask(
            "¿Qué quieres hacer?",
            choices=["habilitar", "deshabilitar", "agregar_comando", "ver_todos"],
            default="ver_todos"
        )
        
        if action == "habilitar":
            security_manager.enable_security()
            console.print("[green]✅ Seguridad habilitada[/green]")
        elif action == "deshabilitar":
            if Confirm.ask("⚠️ ¿Estás seguro? Esto puede ser peligroso"):
                security_manager.disable_security()
                console.print("[yellow]⚠️ Seguridad deshabilitada[/yellow]")
        elif action == "agregar_comando":
            cmd = Prompt.ask("Comando a agregar a la whitelist")
            if security_manager.add_to_whitelist(cmd):
                console.print(f"✅ Comando '{cmd}' agregado a la whitelist")
            else:
                console.print(f"❌ No se pudo agregar '{cmd}' (puede estar en blacklist)")
        elif action == "ver_todos":
            console.print("\n[bold]Todos los comandos permitidos:[/bold]")
            for cmd in sorted(status['whitelist']):
                console.print(f"  • {cmd}")

@cli.command()
def modelos():
    """
    🤖 Lista todos los modelos disponibles
    
    Muestra los 60+ modelos de IA disponibles organizados por categoría.
    """
    available_models = get_available_models('chispart')
    
    # Organizar modelos por categoría
    categories = {
        "OpenAI": [k for k in available_models.keys() if k.startswith('gpt')],
        "Anthropic": [k for k in available_models.keys() if k.startswith('claude')],
        "Meta Llama": [k for k in available_models.keys() if k.startswith('llama')],
        "Google": [k for k in available_models.keys() if k.startswith('gemini')],
        "Mistral": [k for k in available_models.keys() if 'mistral' in k or 'mixtral' in k or 'mathstral' in k],
        "DeepSeek": [k for k in available_models.keys() if k.startswith('deepseek')],
        "Qwen": [k for k in available_models.keys() if k.startswith('qwen')],
        "Código": [k for k in available_models.keys() if 'code' in k or 'starcoder' in k or 'wizard' in k],
        "Otros": [k for k in available_models.keys() if not any(cat in k.lower() for cat in ['gpt', 'claude', 'llama', 'gemini', 'mistral', 'mixtral', 'deepseek', 'qwen', 'code', 'starcoder', 'wizard', 'mathstral'])]
    }
    
    default_model = get_default_model('chispart')
    
    for category, models in categories.items():
        if models:
            console.print(f"\n[bold cyan]🔹 {category}[/bold cyan]")
            for model in sorted(models):
                status = " 🌟" if model == default_model else ""
                console.print(f"  • {model}{status}")
    
    console.print(f"\n[dim]Total: {len(available_models)} modelos disponibles[/dim]")
    console.print(f"[dim]Modelo por defecto: {default_model} 🌟[/dim]")

@cli.command()
def version():
    """
    ℹ️ Información detallada de la versión
    """
    current_profile = profile_manager.get_current_profile()
    security_status = security_manager.get_security_status()
    
    console.print(Panel(
        f"[bold cyan]Chispart Dev Agent v2.1.0[/bold cyan]\n\n"
        f"[bold]🚀 Asistente IA Avanzado para Desarrollo[/bold]\n"
        f"[bold]🏗️ Arquitectura Modular con Perfiles Especializados[/bold]\n\n"
        f"[blue]📊 Estado Actual:[/blue]\n"
        f"• Perfil Activo: {current_profile.name if current_profile else 'Ninguno'}\n"
        f"• Modelos Disponibles: {len(get_available_models('chispart'))}\n"
        f"• Seguridad: {'🟢 Habilitada' if security_status['enabled'] else '🔴 Deshabilitada'}\n"
        f"• Split Chats: {len(split_chat_manager.list_sessions())} activas\n\n"
        f"[green]✨ Características:[/green]\n"
        f"• 7 Perfiles de desarrollo especializados\n"
        f"• Sistema de split/merge chat\n"
        f"• Seguridad con whitelist de comandos\n"
        f"• 60+ modelos de IA potentes\n"
        f"• Ejecución segura de comandos\n"
        f"• Interfaz moderna optimizada\n\n"
        f"[yellow]👨‍💻 Desarrollado por:[/yellow]\n"
        f"Sebastian Vernis Mora",
        title="Información de Versión",
        border_style="cyan"
    ))

if __name__ == "__main__":
    cli()
