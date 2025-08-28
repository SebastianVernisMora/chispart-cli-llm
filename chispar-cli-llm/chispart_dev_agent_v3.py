#!/usr/bin/env python3
"""
Chispart Dev Agent v3.0 - Asistente IA Avanzado para Desarrollo
Incluye: Chat IA, Ejecución de comandos, Equipos, ATC Support, APIs múltiples
"""

import click
import os
import sys
import subprocess
import time
from datetime import datetime
import pty
import select
import termios
from typing import Dict, List, Optional, Any
from pathlib import Path

# Rich imports para interfaz moderna
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

# Imports del proyecto
from config_extended import (
    get_api_config, get_available_models, get_default_model,
    AVAILABLE_APIS, DEFAULT_API, VISION_SUPPORTED_APIS, PDF_SUPPORTED_APIS
)
from api_client import UniversalAPIClient, APIError
from utils import (
    is_supported_image, is_supported_pdf, create_image_data_url,
    extract_text_from_pdf, save_conversation_history, load_conversation_history,
    format_file_size, validate_file_size, log_to_s3
)

# Core modules
from core.dev_profiles import profile_manager
from core.split_chat_manager import split_chat_manager
from core.security_manager import security_manager
from core.theme_manager import theme_manager
from core.conversation_manager import conversation_manager
from core.team_manager import team_manager
from core.atc_agent import atc_agent
from core.command_handler import CommandHandler
from ui.directory_browser import directory_browser

console = Console()

class SecureAPIConfig(dict):
    """Clase personalizada para configuración de API que oculta claves sensibles"""
    
    def __str__(self):
        safe_dict = self.copy()
        if 'api_key' in safe_dict:
            safe_dict['api_key'] = '***'
        return str(safe_dict)
    
    def __repr__(self):
        safe_dict = self.copy()
        if 'api_key' in safe_dict:
            safe_dict['api_key'] = '***'
        return f"SecureAPIConfig({safe_dict})"

def validate_api_key(api_name):
    """
    Valida que la clave API esté configurada para la API especificada
    y sanitiza la clave para prevenir problemas de seguridad.
    Lanza APIError si la validación falla.
    """
    config = get_api_config(api_name)
    
    # Verificar si la clave API está configurada
    if not config["api_key"] or config["api_key"] == "your_api_key_here":
        error_msg = f"Clave API no configurada para {config['name']}.\n" \
                    f"💡 Configura tu clave API como variable de entorno {AVAILABLE_APIS[api_name]['default_key_env']}"
        raise APIError(error_msg, api_name=config['name'])

    # Sanitizar la clave API para prevenir problemas de seguridad
    api_key = config["api_key"]
    
    # Eliminar caracteres nulos (byte 0x00) que pueden causar problemas
    if isinstance(api_key, str) and '\x00' in api_key:
        api_key = api_key.replace('\x00', '')
    
    # Verificar longitud mínima para claves API válidas
    if len(api_key) < 8:
        error_msg = f"Clave API para {config['name']} parece inválida (demasiado corta)."
        raise APIError(error_msg, api_name=config['name'])
    
    # Crear configuración segura
    sanitized_config = SecureAPIConfig(config)
    
    # Reemplazar la clave API con la versión sanitizada
    sanitized_config["api_key"] = api_key
    
    return sanitized_config

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
    """Crea un mensaje con PDF extrayendo el texto"""
    try:
        pdf_text = extract_text_from_pdf(pdf_path)
        filename = os.path.basename(pdf_path)
        
        # Limitar el texto si es muy largo
        max_chars = 100000
        if len(pdf_text) > max_chars:
            pdf_text = pdf_text[:max_chars] + "\n\n[... CONTENIDO TRUNCADO ...]"
        
        full_prompt = f"Se ha extraído el siguiente texto de un documento PDF ('{filename}'):\n\n---\n{pdf_text}\n---\n\nPor favor, responde a la siguiente pregunta basada en el texto del documento:\n\n{text}"
        
        return create_text_message(full_prompt)
    except Exception as e:
        raise click.ClickException(f"Error procesando PDF: {str(e)}")

# Configuración del CLI principal
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--api', '-a', default=DEFAULT_API, 
              type=click.Choice(list(AVAILABLE_APIS.keys())), 
              help='API a utilizar')
@click.version_option(version="3.0.0")
@click.pass_context
def cli(ctx, api):
    """
    🚀 Chispart Dev Agent v3.0 - Asistente IA Avanzado para Desarrollo
    
    ✨ Funcionalidades principales:
    • Chat con IA usando perfiles especializados
    • Ejecución segura de comandos del sistema  
    • Gestión de equipos de desarrollo
    • Asistencia técnica ATC integrada
    • Soporte para múltiples APIs (Chispart, Qwen, Gemini, Codestral)
    • 100+ modelos de IA disponibles
    
    🔧 Comandos principales: chat, execute, perfiles, equipos, ayuda
    """
    ctx.ensure_object(dict)
    ctx.obj['api'] = api

@cli.command()
@click.argument('mensaje')
@click.option('--profile', '-p', help='Perfil de desarrollo a usar')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', help='API específica a usar')
@click.option('--guardar/--no-guardar', default=True, help='Guardar en historial')
@click.pass_context
def chat(ctx, mensaje, profile, modelo, api, guardar):
    """💬 Conversa con IA usando perfiles especializados
    
    Envía mensajes a la IA con contexto especializado según el perfil.
    
    Ejemplos:
    \b
    chispart-dev chat "Crea una API REST" --profile backend
    chispart-dev chat "Optimiza este CSS" --profile frontend --api gemini
    chispart-dev chat "Configura CI/CD" --profile devops --modelo qwen-max
    """
    # Usar API del contexto o la especificada
    api_name = api or ctx.obj['api']
    
    # --- Lógica de envío con fallback ---
    response = None
    client = None
    final_config = {}
    full_message = mensaje

    # --- Primer intento con la API seleccionada ---
    try:
        config = validate_api_key(api_name)
        available_models = get_available_models(api_name)

        if profile:
            if profile not in profile_manager.profiles:
                console.print(f"[red]❌ Perfil no encontrado: {profile}[/red]")
                sys.exit(1)
            profile_info = profile_manager.get_profile(profile)
            console.print(f"[cyan]📋 Usando perfil: {profile_info.name}[/cyan]")
            if not modelo and hasattr(profile_info, 'preferred_models') and profile_info.preferred_models:
                for preferred in profile_info.preferred_models:
                    if preferred in available_models:
                        modelo = preferred
                        break

        if not modelo:
            modelo = get_default_model(api_name)
        elif modelo not in available_models:
            console.print(f"[red]❌ Modelo '{modelo}' no disponible para {config['name']}[/red]")
            sys.exit(1)

        console.print(Panel(f"[bold cyan]API:[/bold cyan] {config['name']}\n[bold green]Modelo:[/bold green] {modelo}\n[bold yellow]Perfil:[/bold yellow] {profile or 'Ninguno'}", title="📤 Intento Principal", border_style="blue"))
        
        if profile:
            full_message = f"{profile_manager.get_profile(profile).system_prompt}\n\nUsuario: {mensaje}"
        
        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        with console.status(f"Enviando a {config['name']}..."):
            response = client.chat_completions([create_text_message(full_message)], available_models[modelo])
        
        final_config = config

    except APIError as e:
        if api_name != DEFAULT_API:
            console.print(f"[yellow]⚠️  La API '{api_name}' falló: {e.message}[/yellow]")
            console.print(f"[yellow]🔄  Intentando con la API de respaldo ({DEFAULT_API})...[/yellow]")

            # --- Intento con API de respaldo ---
            try:
                api_name = DEFAULT_API
                config = validate_api_key(api_name)
                available_models = get_available_models(api_name)
                modelo = get_default_model(api_name)

                console.print(Panel(f"[bold cyan]API:[/bold cyan] {config['name']} (Respaldo)\n[bold green]Modelo:[/bold green] {modelo}\n[bold yellow]Perfil:[/bold yellow] {profile or 'Ninguno'}", title="📤 Intento de Respaldo", border_style="yellow"))

                if profile:
                    full_message = f"{profile_manager.get_profile(profile).system_prompt}\n\nUsuario: {mensaje}"

                client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
                with console.status(f"Enviando a {config['name']}..."):
                    response = client.chat_completions([create_text_message(full_message)], available_models[modelo])

                final_config = config

            except (APIError, Exception) as fallback_e:
                console.print(f"[red]❌ El intento de respaldo también falló: {fallback_e}[/red]")
                sys.exit(1)
        else:
            console.print(f"[red]❌ Error con la API por defecto '{api_name}': {e.message}[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        sys.exit(1)


    # --- Procesar respuesta (si existe) ---
    if response and client and final_config:
        content = client.extract_response_content(response)
        console.print(Panel(Markdown(content), title=f"🤖 Respuesta de {final_config['name']}", border_style="green"))
        
        usage = client.get_usage_info(response)
        if usage:
            console.print(f"\n[dim]💰 Tokens: {usage.get('total_tokens', 'N/A')}[/dim]")
        
        if guardar:
            conversation = {
                "type": "chat", "id": response.get("id"), "api": api_name,
                "model_alias": modelo, "model": response.get("model"),
                "profile": profile, "message": mensaje, "response": content,
                "usage": usage, "timestamp": datetime.now().isoformat()
            }
            save_conversation_history(conversation)
            log_to_s3(conversation)

@cli.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('comando', nargs=-1, type=click.UNPROCESSED)
@click.option('--safe', is_flag=True, help='Ejecutar con validación de seguridad')
@click.option('--timeout', default=60, help='Timeout en segundos')
def execute(comando, safe, timeout):
    """⚡ Ejecuta comandos del sistema con PTY real
    
    Ejecuta comandos con validación de seguridad, streaming de salida,
    y manejo de timeouts.
    
    Ejemplos:
    \b
    chispart-dev execute -- "git status"
    chispart-dev execute -- safe -- "ls -la"
    chispart-dev execute -- timeout=10 -- "ping 8.8.8.8"
    """
    if not comando:
        console.print("[red]❌ No se ha especificado ningún comando para ejecutar.[/red]")
        return

    full_command = " ".join(comando)

    if safe:
        validation = security_manager.validate_command(full_command)
        if not validation.is_allowed:
            console.print(Panel(
                f"[red]❌ Comando no permitido[/red]\n\n"
                f"[yellow]Razón:[/yellow] {validation.reason}\n\n"
                f"[blue]Comando:[/blue] {full_command}",
                title="🛡️ Seguridad",
                border_style="red"
            ))
            return
    
    console.print(Panel(
        f"[bold green]Ejecutando:[/bold green] {full_command}\n"
        f"[dim]Timeout: {timeout}s[/dim]",
        title="⚡ Ejecución de Comando",
        border_style="blue"
    ))

    try:
        pid, fd = pty.fork()
    except OSError as e:
        console.print(f"[red]❌ Error al crear el pty: {e}[/red]")
        return

    if pid == 0:  # Proceso hijo
        try:
            # Si el comando es una sola cadena, usar shell para interpretarlo
            if len(comando) == 1:
                os.execv('/bin/sh', ['/bin/sh', '-c', comando[0]])
            else:
                os.execvp(comando[0], comando)
        except FileNotFoundError:
            print(f"Comando no encontrado: {comando[0]}")
            os._exit(127)
        except Exception as e:
            print(f"Error ejecutando comando: {e}")
            os._exit(1)

    # Proceso padre
    start_time = time.time()
    output_buffer = b''

    try:
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                console.print(f"\n[red]❌ Comando excedió el timeout de {timeout}s[/red]")
                os.kill(pid, 9)
                break

            try:
                r, _, _ = select.select([fd], [], [], 0.1)
                if r:
                    data = os.read(fd, 1024)
                    if not data:
                        break  # EOF

                    # Escribir directamente a la salida estándar del sistema
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
                    output_buffer += data
            except OSError:
                break
    finally:
        # Esperar al proceso hijo y obtener su código de salida
        try:
            wait_pid, exit_status = os.waitpid(pid, 0)
            exit_code = os.WEXITSTATUS(exit_status) if os.WIFEXITED(exit_status) else 1
            
            console.print(f"\n[bold {'green' if exit_code == 0 else 'red'}]"
                          f"✅ Proceso finalizado con código de salida: {exit_code}"
                          f"[/bold {'green' if exit_code == 0 else 'red'}]")

        except ChildProcessError:
            # Esto puede ocurrir si el proceso fue terminado (ej. por timeout)
            console.print(f"\n[bold red]✅ Proceso finalizado (terminado a la fuerza)[/bold red]")

        os.close(fd)

@cli.command()
@click.option('--interactive', '-i', is_flag=True, help='Modo interactivo')
def perfiles(interactive):
    """👥 Gestiona perfiles de desarrollo especializados
    
    Lista y configura perfiles para diferentes roles de desarrollo.
    """
    profile_manager.display_profiles_table()
    
    if interactive:
        profile_manager.interactive_profile_selection()

@cli.command()
@click.option('--api', '-a', help='API específica para mostrar modelos')
@click.option('--categoria', '-c', help='Filtrar por categoría')
@click.pass_context
def modelos(ctx, api, categoria):
    """🤖 Lista modelos de IA disponibles
    
    Muestra todos los modelos disponibles organizados por API y categoría.
    """
    api_name = api or ctx.obj['api']
    config = get_api_config(api_name)
    available_models = get_available_models(api_name)
    
    # Crear tabla de modelos
    table = Table(title=f"🤖 Modelos Disponibles - {config['name']}")
    table.add_column("Modelo", style="cyan", width=25)
    table.add_column("ID Técnico", style="green", width=40)
    table.add_column("Categoría", style="yellow", width=15)
    
    # Categorizar modelos
    categories = {
        "gpt": "OpenAI",
        "claude": "Anthropic", 
        "llama": "Meta",
        "gemini": "Google",
        "mixtral": "Mistral",
        "deepseek": "DeepSeek",
        "qwen": "Qwen",
        "codellama": "Código",
        "starcoder": "Código",
        "wizardcoder": "Código",
        "mathstral": "Matemáticas"
    }
    
    model_count = 0
    for name, model_id in available_models.items():
        # Determinar categoría
        model_category = "Otros"
        for key, cat in categories.items():
            if key in name.lower():
                model_category = cat
                break
        
        # Filtrar por categoría si se especifica
        if categoria and categoria.lower() not in model_category.lower():
            continue
            
        table.add_row(name, model_id, model_category)
        model_count += 1
    
    console.print(table)
    
    # Mostrar estadísticas
    default_model = get_default_model(api_name)
    console.print(f"\n[dim]📊 Total de modelos: {model_count}[/dim]")
    console.print(f"[dim]⭐ Modelo por defecto: {default_model}[/dim]")
    
    if not categoria:
        console.print(f"[dim]💡 Usa --categoria para filtrar (ej: --categoria OpenAI)[/dim]")

@cli.command()
@click.option('--crear', '-c', is_flag=True, help='Crear nuevo equipo')
@click.option('--detalle', '-d', help='Ver detalles de un equipo específico')
@click.option('--activar', '-a', help='Activar un equipo para uso')
def equipos(crear, detalle, activar):
    """🏗️ Gestiona equipos de desarrollo
    
    Crea, lista y gestiona equipos de desarrollo con miembros especializados.
    """
    if crear:
        _crear_equipo_interactivo()
    elif detalle:
        team_manager.display_team_details(detalle)
    elif activar:
        try:
            team_manager.activate_team(activar)
            console.print(f"[green]✅ Equipo '{activar}' activado[/green]")
        except ValueError as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    else:
        team_manager.display_teams_table()

def _crear_equipo_interactivo():
    """Proceso interactivo para crear un equipo"""
    console.print("[bold green]🏗️ Crear Nuevo Equipo de Desarrollo[/bold green]")
    
    name = Prompt.ask("Nombre del equipo")
    description = Prompt.ask("Descripción del equipo")
    
    # Tipo de proyecto
    project_types = ["web", "mobile", "api", "fullstack", "desktop", "data", "devops"]
    console.print("\nTipos de proyecto disponibles:")
    for i, ptype in enumerate(project_types, 1):
        console.print(f"  {i}. {ptype}")
    
    project_choice = Prompt.ask("Selecciona tipo de proyecto", choices=[str(i) for i in range(1, len(project_types)+1)])
    project_type = project_types[int(project_choice) - 1]
    
    # Tech stack
    console.print("\nTech stack (separado por comas):")
    tech_stack_input = Prompt.ask("Tecnologías", default="Python, JavaScript, Docker")
    tech_stack = [tech.strip() for tech in tech_stack_input.split(",")]
    
    # APIs preferidas
    available_apis = list(AVAILABLE_APIS.keys())
    console.print(f"\nAPIs disponibles: {', '.join(available_apis)}")
    apis_input = Prompt.ask("APIs preferidas (separadas por comas)", default="chispart")
    preferred_apis = [api.strip() for api in apis_input.split(",")]
    
    try:
        team_id = team_manager.create_team(name, description, project_type, tech_stack, preferred_apis)
        console.print(f"[green]✅ Equipo '{name}' creado con ID: {team_id}[/green]")
        
        # Preguntar si quiere añadir miembros
        if Confirm.ask("¿Quieres añadir miembros al equipo?"):
            _añadir_miembros_interactivo(team_id)
            
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")

def _añadir_miembros_interactivo(team_id: str):
    """Proceso interactivo para añadir miembros"""
    profiles = list(profile_manager.profiles.keys())
    
    while True:
        console.print(f"\n[bold cyan]Añadir Miembro al Equipo[/bold cyan]")
        
        name = Prompt.ask("Nombre del miembro")
        
        # Perfil
        console.print("\nPerfiles disponibles:")
        for i, profile in enumerate(profiles, 1):
            console.print(f"  {i}. {profile}")
        
        profile_choice = Prompt.ask("Selecciona perfil", choices=[str(i) for i in range(1, len(profiles)+1)])
        profile = profiles[int(profile_choice) - 1]
        
        # Rol
        roles = ["junior", "mid", "senior", "lead", "architect"]
        console.print(f"\nRoles disponibles: {', '.join(roles)}")
        role = Prompt.ask("Rol", choices=roles, default="mid")
        
        # Especialidades
        specialties_input = Prompt.ask("Especialidades (separadas por comas)", default="desarrollo, testing")
        specialties = [spec.strip() for spec in specialties_input.split(",")]
        
        # Modelos preferidos
        preferred_models_input = Prompt.ask("Modelos preferidos (separados por comas)", default="gpt-4, claude-3.5-sonnet")
        preferred_models = [model.strip() for model in preferred_models_input.split(",")]
        
        try:
            team_manager.add_member(team_id, name, profile, role, specialties, preferred_models)
            console.print(f"[green]✅ Miembro '{name}' añadido al equipo[/green]")
        except ValueError as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        
        if not Confirm.ask("¿Añadir otro miembro?"):
            break

@cli.command()
@click.argument('problema', required=False)
@click.option('--interactivo', '-i', is_flag=True, help='Modo interactivo paso a paso')
@click.option('--diagnostico', '-d', is_flag=True, help='Solo ejecutar diagnósticos')
def ayuda(problema, interactivo, diagnostico):
    """🆘 Asistencia Técnica Chispart (ATC)
    
    Agente experto interno para soporte y resolución de problemas.
    Proporciona diagnóstico automático y guía paso a paso.
    
    Ejemplos:
    \b
    chispart-dev ayuda "No puedo conectar con la API"
    chispart-dev ayuda --interactivo
    chispart-dev ayuda --diagnostico
    """
    if not problema and not interactivo and not diagnostico:
        # Mostrar guía de ayuda
        atc_agent.show_help_guide()
        return
    
    if diagnostico:
        # Solo ejecutar diagnósticos
        console.print("[bold blue]🔍 Ejecutando Diagnósticos del Sistema...[/bold blue]")
        session_id = atc_agent.start_support_session("Diagnóstico general del sistema")
        diagnostics = atc_agent.run_diagnostics()
        suggestions = atc_agent.analyze_and_suggest()
        
        if suggestions:
            console.print("\n[bold yellow]💡 Sugerencias Encontradas:[/bold yellow]")
            for suggestion in suggestions:
                console.print(f"  • {suggestion}")
        else:
            console.print("\n[green]✅ No se detectaron problemas evidentes[/green]")
        return
    
    if problema:
        # Iniciar sesión de soporte con problema específico
        session_id = atc_agent.start_support_session(problema)
        
        if interactivo:
            atc_agent.interactive_troubleshooting()
        else:
            # Diagnóstico automático
            diagnostics = atc_agent.run_diagnostics()
            suggestions = atc_agent.analyze_and_suggest()
            
            if suggestions:
                console.print("\n[bold yellow]💡 Sugerencias de Solución:[/bold yellow]")
                for i, suggestion in enumerate(suggestions, 1):
                    console.print(f"  {i}. {suggestion}")
                
                console.print(f"\n[dim]Para resolución interactiva, usa: chispart-dev ayuda \"{problema}\" --interactivo[/dim]")
            else:
                console.print("\n[yellow]No se encontraron sugerencias automáticas.[/yellow]")
                console.print(f"[dim]Para diagnóstico manual, usa: chispart-dev ayuda \"{problema}\" --interactivo[/dim]")
    
    elif interactivo:
        # Modo interactivo sin problema específico
        problema_input = Prompt.ask("Describe el problema que estás experimentando")
        session_id = atc_agent.start_support_session(problema_input)
        atc_agent.interactive_troubleshooting()

@cli.command()
@click.option('--interactive', '-i', is_flag=True, help='Modo interactivo')
def security(interactive):
    """🛡️ Gestiona la configuración de seguridad
    
    Muestra y configura las opciones de seguridad del sistema.
    """
    # Obtener estado de seguridad
    status = security_manager.get_security_status()
    
    # Mostrar información de seguridad
    security_info = Panel(
        f"[bold cyan]🛡️ Estado de Seguridad[/bold cyan]\n\n"
        f"[bold green]Sistema habilitado:[/bold green] {'✅ Sí' if status['enabled'] else '❌ No'}\n"
        f"[bold yellow]Plan de usuario:[/bold yellow] {status['plan'].capitalize()}\n"
        f"[bold yellow]Comandos permitidos:[/bold yellow] {status['whitelist_count']}\n"
        f"[bold red]Comandos bloqueados:[/bold red] {status['blacklist_count']}\n"
        f"[bold blue]Requieren confirmación:[/bold blue] {status['confirmation_required_count']}\n\n"
        f"[bold magenta]Configuración:[/bold magenta]\n"
        f"• Whitelist activa: {'✅' if status['enabled'] else '❌'}\n"
        f"• Validación de patrones: ✅\n"
        f"• Timeout de comandos: 30s\n"
        f"• Sandboxing: ✅",
        title="🔒 Configuración de Seguridad",
        border_style="blue"
    )
    console.print(security_info)
    
    # Mostrar algunos comandos de cada categoría
    console.print("\n[bold green]✅ Comandos Permitidos (algunos):[/bold green]")
    allowed_sample = sorted(status['whitelist'])[:10]
    for cmd in allowed_sample:
        console.print(f"  • {cmd}")
    
    console.print(f"\n[dim]... y {status['whitelist_count'] - 10} más[/dim]")
    
    console.print("\n[bold red]❌ Comandos Bloqueados (algunos):[/bold red]")
    blocked_sample = sorted(status['blacklist'])[:10]
    for cmd in blocked_sample:
        console.print(f"  • {cmd}")
    
    console.print(f"\n[dim]... y {status['blacklist_count'] - 10} más[/dim]")
    
    if interactive:
        console.print("\n[bold yellow]⚙️ Configuración Interactiva[/bold yellow]")
        
        action = Prompt.ask(
            "¿Qué quieres hacer?",
            choices=["habilitar", "deshabilitar", "ver_todos"],
            default="ver_todos"
        )
        
        if action == "habilitar":
            security_manager.enable_security()
            console.print("[green]✅ Seguridad habilitada[/green]")
        elif action == "deshabilitar":
            if Confirm.ask("⚠️ ¿Estás seguro de deshabilitar la seguridad?"):
                security_manager.disable_security()
                console.print("[yellow]⚠️ Seguridad deshabilitada[/yellow]")
        elif action == "ver_todos":
            console.print("\n[bold]Todos los comandos permitidos:[/bold]")
            for cmd in sorted(status['whitelist']):
                console.print(f"  • {cmd}")

@cli.command()
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', help='API específica a usar')
@click.pass_context
def interactivo(ctx, modelo, api):
    """🗣️ Inicia una sesión de chat interactiva persistente
    
    Características:
    • Conversación continua con contexto
    • Comandos especiales integrados
    • Estadísticas de sesión en tiempo real
    • Historial persistente entre sesiones
    
    Comandos especiales en sesión:
    'salir', 'exit', 'quit' - Terminar sesión
    'limpiar', 'clear' - Limpiar contexto
    'stats' - Ver estadísticas de sesión
    'historial' - Ver historial de conversación
    
    Ejemplos:
    \b
    chispart-dev interactivo
    chispart-dev interactivo --modelo gpt-4 --api chispart
    """
    # Usar API del contexto o la especificada
    api_name = api or ctx.obj['api']
    
    # Validar API
    config = validate_api_key(api_name)
    available_models = get_available_models(api_name)
    
    # Determinar modelo
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]❌ Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(list(available_models.keys())[:10])}...[/yellow]")
        sys.exit(1)
    
    # Mostrar información de la sesión
    session_info = Panel(
        f"[bold cyan]🗣️ Sesión Interactiva Iniciada[/bold cyan]\n\n"
        f"[bold green]API:[/bold green] {config['name']}\n"
        f"[bold yellow]Modelo:[/bold yellow] {modelo}\n"
        f"[bold blue]Comandos especiales:[/bold blue] salir, limpiar, stats, historial, comandos\n"
        f"[bold magenta]Análisis de directorios:[/bold magenta] @analizar, @explorar, navegador\n"
        f"[bold cyan]Persistencia:[/bold cyan] Activada",
        title="🚀 Modo Interactivo Avanzado",
        border_style="green"
    )
    console.print(session_info)
    
    # Crear cliente
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    model_name = available_models[modelo]
    
    # Variables de sesión
    conversation_history = []
    session_stats = {
        "messages_sent": 0,
        "total_tokens": 0,
        "session_start": datetime.now()
    }
    
    # Cargar historial previo si existe
    try:
        previous_history = load_conversation_history()
        if previous_history:
            # Cargar las últimas 10 conversaciones para contexto
            recent_conversations = previous_history[-10:]
            for conv in recent_conversations:
                if conv.get("type") == "chat":
                    conversation_history.append({
                        "role": "user",
                        "content": conv.get("message", "")
                    })
                    conversation_history.append({
                        "role": "assistant", 
                        "content": conv.get("response", "")
                    })
            console.print(f"[dim]📚 Cargado contexto de {len(recent_conversations)} conversaciones previas[/dim]")
    except Exception as e:
        console.print(f"[yellow]⚠️ No se pudo cargar historial previo: {e}[/yellow]")
    
    console.print(f"\n[green]💬 ¡Sesión interactiva iniciada! Escribe tu mensaje o usa comandos especiales.[/green]")
    console.print(f"[dim]Escribe 'salir' para terminar la sesión.[/dim]\n")
    
    try:
        while True:
            # Solicitar entrada del usuario
            try:
                user_input = Prompt.ask(f"[bold cyan]Tú[/bold cyan]", console=console)
            except KeyboardInterrupt:
                console.print("\n[yellow]Sesión interrumpida. ¡Hasta luego![/yellow]")
                break
            
            # Procesar comandos especiales
            if user_input.lower() in ['salir', 'exit', 'quit']:
                console.print("[green]👋 ¡Hasta luego! Sesión guardada.[/green]")
                break
            elif user_input.lower() in ['limpiar', 'clear']:
                conversation_history = []
                console.print("[yellow]🧹 Contexto de conversación limpiado.[/yellow]")
                continue
            elif user_input.lower() == 'stats':
                duration = datetime.now() - session_stats["session_start"]
                stats_panel = Panel(
                    f"[bold cyan]📊 Estadísticas de Sesión[/bold cyan]\n\n"
                    f"[bold green]Mensajes enviados:[/bold green] {session_stats['messages_sent']}\n"
                    f"[bold yellow]Tokens utilizados:[/bold yellow] {session_stats['total_tokens']}\n"
                    f"[bold blue]Duración:[/bold blue] {str(duration).split('.')[0]}\n"
                    f"[bold magenta]Contexto actual:[/bold magenta] {len(conversation_history)} mensajes",
                    title="📈 Estadísticas",
                    border_style="blue"
                )
                console.print(stats_panel)
                continue
            elif user_input.lower() == 'historial':
                if conversation_history:
                    console.print("[bold cyan]📚 Historial de la sesión actual:[/bold cyan]")
                    for i, msg in enumerate(conversation_history[-10:], 1):
                        role = "🧑 Usuario" if msg["role"] == "user" else "🤖 IA"
                        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        console.print(f"[dim]{i}. {role}:[/dim] {content}")
                else:
                    console.print("[yellow]📭 No hay historial en esta sesión.[/yellow]")
                continue
            elif user_input.lower() == 'navegador':
                console.print("[cyan]🗂️ Abriendo navegador de directorios...[/cyan]")
                try:
                    directory_browser.start_interactive_session()
                except Exception as e:
                    console.print(f"[red]❌ Error en navegador: {str(e)}[/red]")
                continue
            elif user_input.startswith('@analizar '):
                # Comando especial para análisis de directorio
                directory_path = user_input[10:].strip()
                if not directory_path:
                    console.print("[red]❌ Especifica una ruta de directorio[/red]")
                    continue
                
                console.print(f"[cyan]🔍 Analizando directorio: {directory_path}[/cyan]")
                try:
                    command_handler = CommandHandler()
                    result = command_handler.handle_directory_analysis(
                        api_name=api_name,
                        directory_path=directory_path,
                        model=modelo,
                        save_history=False  # No guardar para evitar duplicados
                    )
                    
                    if result["success"]:
                        # Añadir contexto del análisis a la conversación
                        analysis_summary = f"He analizado el directorio '{directory_path}'. Aquí tienes un resumen:\n\n{result['structural_analysis']['summary']}\n\nAnálisis IA:\n{result['ai_analysis']}"
                        
                        conversation_history.append({
                            "role": "assistant",
                            "content": analysis_summary
                        })
                        
                        session_stats["messages_sent"] += 1
                        if result.get("usage") and result["usage"].get("total_tokens"):
                            session_stats["total_tokens"] += result["usage"]["total_tokens"]
                    else:
                        console.print(f"[red]❌ Error en análisis: {result.get('error', 'Error desconocido')}[/red]")
                        
                except Exception as e:
                    console.print(f"[red]❌ Error en análisis: {str(e)}[/red]")
                continue
            elif user_input.startswith('@explorar '):
                # Comando especial para exploración de código
                parts = user_input[10:].strip().split(' --enfoque ')
                directory_path = parts[0].strip()
                focus_area = parts[1].strip() if len(parts) > 1 else 'general'
                
                if not directory_path:
                    console.print("[red]❌ Especifica una ruta de directorio[/red]")
                    continue
                
                console.print(f"[cyan]🔍 Explorando código en: {directory_path} (enfoque: {focus_area})[/cyan]")
                try:
                    command_handler = CommandHandler()
                    result = command_handler.handle_codebase_exploration(
                        api_name=api_name,
                        directory_path=directory_path,
                        focus_area=focus_area,
                        model=modelo,
                        save_history=False
                    )
                    
                    if result["success"]:
                        # Añadir contexto del análisis a la conversación
                        exploration_summary = f"He explorado el codebase en '{directory_path}' con enfoque en {focus_area}:\n\n{result['analysis']}"
                        
                        conversation_history.append({
                            "role": "assistant",
                            "content": exploration_summary
                        })
                        
                        session_stats["messages_sent"] += 1
                    else:
                        console.print(f"[red]❌ Error en exploración: {result.get('error', 'Error desconocido')}[/red]")
                        
                except Exception as e:
                    console.print(f"[red]❌ Error en exploración: {str(e)}[/red]")
                continue
            elif user_input.lower() == 'comandos':
                # Mostrar comandos especiales disponibles
                commands_help = f"""
[bold cyan]🔧 Comandos Especiales Disponibles:[/bold cyan]

[bold yellow]Básicos:[/bold yellow]
[dim]• salir, exit, quit - Terminar sesión[/dim]
[dim]• limpiar, clear - Limpiar contexto[/dim]
[dim]• stats - Ver estadísticas de sesión[/dim]
[dim]• historial - Ver historial de conversación[/dim]
[dim]• comandos - Mostrar esta ayuda[/dim]

[bold yellow]Análisis de Directorios:[/bold yellow]
[dim]• @analizar <ruta> - Analizar directorio completo[/dim]
[dim]• @explorar <ruta> --enfoque <tipo> - Explorar código especializado[/dim]
[dim]• navegador - Abrir navegador interactivo[/dim]

[bold yellow]Ejemplos:[/bold yellow]
[dim]• @analizar ./mi-proyecto[/dim]
[dim]• @explorar . --enfoque security[/dim]
[dim]• @explorar /path/code --enfoque architecture[/dim]

[bold green]💡 Tip:[/bold green] Los análisis se integran automáticamente en la conversación
"""
                console.print(Panel(
                    commands_help.strip(),
                    title="📚 Ayuda de Comandos",
                    border_style="blue"
                ))
                continue
            
            if not user_input.strip():
                continue
            
            # Agregar mensaje del usuario al historial
            conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            try:
                # Enviar mensaje con contexto
                with console.status(f"[bold green]🤖 {config['name']} está pensando..."):
                    response = client.chat_completions(conversation_history, model_name)
                
                # Extraer respuesta
                content = client.extract_response_content(response)
                
                # Mostrar respuesta
                console.print(f"\n[bold green]🤖 {config['name']}:[/bold green]")
                console.print(Panel(
                    Markdown(content),
                    border_style="green",
                    padding=(1, 2)
                ))
                
                # Agregar respuesta al historial
                conversation_history.append({
                    "role": "assistant",
                    "content": content
                })
                
                # Actualizar estadísticas
                session_stats["messages_sent"] += 1
                usage = client.get_usage_info(response)
                if usage and usage.get('total_tokens'):
                    session_stats["total_tokens"] += usage.get('total_tokens', 0)
                
                # Guardar conversación en historial persistente
                conversation_data = {
                    "type": "interactive_chat",
                    "api": api_name,
                    "model": modelo,
                    "message": user_input,
                    "response": content,
                    "usage": usage,
                    "timestamp": datetime.now().isoformat()
                }
                save_conversation_history(conversation_data)
                
                # Mostrar información de uso si está disponible
                if usage and usage.get('total_tokens'):
                    console.print(f"[dim]💰 Tokens: {usage.get('total_tokens', 'N/A')} | Total sesión: {session_stats['total_tokens']}[/dim]")
                
                print()  # Línea en blanco para separar
                
            except APIError as e:
                console.print(f"[red]❌ Error de {e.api_name}: {e.message}[/red]")
                if e.status_code:
                    console.print(f"[red]Código de estado: {e.status_code}[/red]")
            except Exception as e:
                console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Sesión interrumpida. ¡Hasta luego![/yellow]")
    
    # Mostrar resumen final
    duration = datetime.now() - session_stats["session_start"]
    final_stats = Panel(
        f"[bold cyan]📊 Resumen de Sesión[/bold cyan]\n\n"
        f"[bold green]Mensajes enviados:[/bold green] {session_stats['messages_sent']}\n"
        f"[bold yellow]Tokens utilizados:[/bold yellow] {session_stats['total_tokens']}\n"
        f"[bold blue]Duración total:[/bold blue] {str(duration).split('.')[0]}\n"
        f"[bold magenta]Conversaciones guardadas:[/bold magenta] ✅ Persistente",
        title="🏁 Sesión Finalizada",
        border_style="blue"
    )
    console.print(final_stats)

@cli.command()
@click.argument('directorio')
@click.option('--prompt', '-p', default="Analiza este directorio y proporciona insights sobre la estructura del proyecto", help='Prompt personalizado para el análisis')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', help='API específica a usar')
@click.option('--profundidad', '--depth', type=int, help='Profundidad máxima de análisis')
@click.option('--incluir-ocultos', is_flag=True, help='Incluir archivos y directorios ocultos')
@click.option('--sin-contenido', is_flag=True, help='No analizar contenido de archivos')
@click.pass_context
def analizar_directorio(ctx, directorio, prompt, modelo, api, profundidad, incluir_ocultos, sin_contenido):
    """🔍 Analiza un directorio completo y proporciona insights sobre la estructura del proyecto
    
    Realiza un análisis estructural del directorio y utiliza IA para proporcionar
    insights detallados sobre la arquitectura, patrones y recomendaciones.
    
    Ejemplos:
    \b
    chispart-dev analizar-directorio ./mi-proyecto
    chispart-dev analizar-directorio /home/user/codigo --profundidad 5
    chispart-dev analizar-directorio . --prompt "Evalúa la seguridad del código"
    """
    # Usar API del contexto o la especificada
    api_name = api or ctx.obj['api']
    
    # Validar API
    config = validate_api_key(api_name)
    
    # Crear manejador de comandos
    command_handler = CommandHandler()
    
    try:
        console.print(f"[bold cyan]🔍 Analizando directorio: {directorio}[/bold cyan]")
        
        result = command_handler.handle_directory_analysis(
            api_name=api_name,
            directory_path=directorio,
            prompt=prompt,
            model=modelo,
            max_depth=profundidad,
            include_hidden=incluir_ocultos,
            analyze_content=not sin_contenido,
            save_history=True
        )
        
        if not result["success"]:
            console.print(f"[red]❌ Error en análisis: {result.get('error', 'Error desconocido')}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('directorio')
@click.option('--enfoque', '-e', 
              type=click.Choice(['general', 'architecture', 'security', 'performance', 'testing']),
              default='general',
              help='Área de enfoque para la exploración')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', help='API específica a usar')
@click.pass_context
def explorar_codigo(ctx, directorio, enfoque, modelo, api):
    """🔍 Explora un codebase con enfoque especializado
    
    Realiza una exploración especializada del código enfocándose en áreas específicas
    como arquitectura, seguridad, rendimiento o testing.
    
    Ejemplos:
    \b
    chispart-dev explorar-codigo ./proyecto --enfoque architecture
    chispart-dev explorar-codigo . --enfoque security --modelo gpt-4
    chispart-dev explorar-codigo /path/to/code --enfoque performance
    """
    # Usar API del contexto o la especificada
    api_name = api or ctx.obj['api']
    
    # Validar API
    config = validate_api_key(api_name)
    
    # Crear manejador de comandos
    command_handler = CommandHandler()
    
    try:
        console.print(f"[bold cyan]🔍 Explorando codebase con enfoque en: {enfoque}[/bold cyan]")
        
        result = command_handler.handle_codebase_exploration(
            api_name=api_name,
            directory_path=directorio,
            focus_area=enfoque,
            model=modelo,
            save_history=True
        )
        
        if not result["success"]:
            console.print(f"[red]❌ Error en exploración: {result.get('error', 'Error desconocido')}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('directorio')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', help='API específica a usar')
@click.pass_context
def patrones_proyecto(ctx, directorio, modelo, api):
    """🏗️ Analiza patrones de arquitectura y diseño del proyecto
    
    Identifica patrones de diseño, arquitectura y mejores prácticas utilizadas
    en el proyecto, proporcionando recomendaciones específicas.
    
    Ejemplos:
    \b
    chispart-dev patrones-proyecto ./mi-app
    chispart-dev patrones-proyecto . --modelo claude-3.5-sonnet
    """
    # Usar API del contexto o la especificada
    api_name = api or ctx.obj['api']
    
    # Validar API
    config = validate_api_key(api_name)
    
    # Crear manejador de comandos
    command_handler = CommandHandler()
    
    try:
        console.print(f"[bold cyan]🏗️ Analizando patrones de arquitectura...[/bold cyan]")
        
        result = command_handler.handle_project_patterns_analysis(
            api_name=api_name,
            directory_path=directorio,
            model=modelo
        )
        
        if not result["success"]:
            console.print(f"[red]❌ Error en análisis de patrones: {result.get('error', 'Error desconocido')}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
def navegador():
    """🗂️ Inicia el navegador interactivo de directorios
    
    Abre una interfaz interactiva para navegar, explorar y analizar directorios
    con comandos especializados y capacidades de análisis integradas.
    
    Funcionalidades:
    • Navegación interactiva de directorios
    • Análisis estructural en tiempo real
    • Visualización de árboles de archivos
    • Sistema de marcadores
    • Información detallada de archivos y directorios
    """
    try:
        directory_browser.start_interactive_session()
    except Exception as e:
        console.print(f"[red]❌ Error en navegador: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
def playground():
    """🎮 Inicia el playground interactivo de aprendizaje
    
    Sistema de tutorial interactivo que enseña todos los comandos de Chispart CLI
    con ejemplos prácticos y un entorno seguro de aprendizaje.
    
    Funcionalidades:
    • Tutorial paso a paso de todos los comandos
    • Ejemplos prácticos con datos de muestra
    • Entorno seguro para experimentar
    • Progreso guardado automáticamente
    • 7 módulos de aprendizaje especializados
    """
    try:
        # Importar el playground
        from ui.interactive_playground import start_playground
        
        console.print("[bold green]🎮 Iniciando Playground Interactivo...[/bold green]")
        start_playground()
        
    except ImportError as e:
        console.print(f"[red]❌ Error importando playground: {e}[/red]")
        console.print("[yellow]💡 Asegúrate de que el módulo ui.interactive_playground esté disponible[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error iniciando playground: {str(e)}[/red]")

@cli.command()
def version():
    """📋 Muestra información de versión y sistema"""
    console.print(Panel(
        f"[bold green]🚀 Chispart Dev Agent v3.0[/bold green]\n\n"
        f"[bold cyan]Funcionalidades:[/bold cyan]\n"
        f"• 💬 Chat con IA (100+ modelos)\n"
        f"• ⚡ Ejecución segura de comandos\n"
        f"• 👥 Perfiles especializados (7 tipos)\n"
        f"• 🏗️ Gestión de equipos de desarrollo\n"
        f"• 🆘 Asistencia técnica ATC\n"
        f"• 🛡️ Sistema de seguridad robusto\n"
        f"• 🗣️ Modo interactivo persistente\n"
        f"• 🔍 Análisis de directorios y codebase\n"
        f"• 🗂️ Navegador interactivo de archivos\n"
        f"• 🎮 Playground interactivo de aprendizaje\n\n"
        f"[bold yellow]APIs Soportadas:[/bold yellow]\n"
        f"• Chispart (BlackboxAI) - 60+ modelos\n"
        f"• Qwen AI - Modelos especializados\n"
        f"• Google Gemini - Multimodal\n"
        f"• Mistral Codestral - Código\n\n"
        f"[bold blue]Desarrollado por:[/bold blue] Sebastian Vernis | Soluciones Digitales\n"
        f"[bold magenta]Licencia:[/bold magenta] MIT",
        title="📋 Información del Sistema",
        border_style="blue"
    ))

if __name__ == "__main__":
    cli()
