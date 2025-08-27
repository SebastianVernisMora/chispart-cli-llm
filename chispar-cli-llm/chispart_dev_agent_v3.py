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
    format_file_size, validate_file_size
)

# Core modules
from core.dev_profiles import profile_manager
from core.split_chat_manager import split_chat_manager
from core.security_manager import security_manager
from core.theme_manager import theme_manager
from core.conversation_manager import conversation_manager
from core.team_manager import team_manager
from core.atc_agent import atc_agent

console = Console()

def validate_api_key(api_name):
    """Valida que la clave API esté configurada para la API especificada"""
    config = get_api_config(api_name)
    if not config["api_key"] or config["api_key"] == "your_api_key_here":
        console.print(f"[red]❌ Error: Clave API no configurada para {config['name']}.[/red]")
        console.print(f"[yellow]💡 Configura tu clave API como variable de entorno {AVAILABLE_APIS[api_name]['default_key_env']}[/yellow]")
        console.print(f"[dim]Ejemplo: export {AVAILABLE_APIS[api_name]['default_key_env']}='tu_clave_aqui'[/dim]")
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
    
    # Validar API
    config = validate_api_key(api_name)
    available_models = get_available_models(api_name)
    
    # Aplicar perfil si se especifica
    if profile:
        if profile not in profile_manager.profiles:
            console.print(f"[red]❌ Perfil no encontrado: {profile}[/red]")
            console.print(f"[yellow]Perfiles disponibles: {', '.join(profile_manager.profiles.keys())}[/yellow]")
            sys.exit(1)
        
        profile_info = profile_manager.get_profile(profile)
        console.print(f"[cyan]📋 Usando perfil: {profile_info['name']}[/cyan]")
        
        # Usar modelo preferido del perfil si no se especifica otro
        if not modelo and profile_info.get('preferred_models'):
            for preferred in profile_info['preferred_models']:
                if preferred in available_models:
                    modelo = preferred
                    break
    
    # Determinar modelo
    if not modelo:
        modelo = get_default_model(api_name)
    elif modelo not in available_models:
        console.print(f"[red]❌ Modelo '{modelo}' no disponible para {config['name']}[/red]")
        console.print(f"[yellow]Modelos disponibles: {', '.join(list(available_models.keys())[:10])}...[/yellow]")
        sys.exit(1)
    
    # Mostrar información del chat
    chat_info = Panel(
        f"[bold cyan]API:[/bold cyan] {config['name']}\n"
        f"[bold green]Modelo:[/bold green] {modelo}\n"
        f"[bold yellow]Perfil:[/bold yellow] {profile or 'Ninguno'}\n"
        f"[bold blue]Mensaje:[/bold blue] {mensaje}",
        title="📤 Chat",
        border_style="blue"
    )
    console.print(chat_info)
    
    # Preparar mensaje con contexto de perfil
    if profile:
        profile_info = profile_manager.get_profile(profile)
        system_prompt = profile_info.get('system_prompt', '')
        full_message = f"{system_prompt}\n\nUsuario: {mensaje}"
    else:
        full_message = mensaje
    
    # Crear cliente y enviar mensaje
    client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
    
    try:
        with console.status(f"[bold green]Enviando mensaje a {config['name']}..."):
            messages = [create_text_message(full_message)]
            model_name = available_models[modelo]
            response = client.chat_completions(messages, model_name)
        
        # Mostrar respuesta
        content = client.extract_response_content(response)
        
        console.print(Panel(
            Markdown(content),
            title=f"[bold blue]🤖 Respuesta de {config['name']}[/bold blue]",
            border_style="green"
        ))
        
        # Mostrar información de uso
        usage = client.get_usage_info(response)
        if usage:
            console.print(f"\n[dim]💰 Tokens utilizados: {usage.get('total_tokens', 'N/A')}[/dim]")
        
        # Guardar en historial
        if guardar:
            conversation = {
                "type": "chat",
                "api": api_name,
                "model": modelo,
                "profile": profile,
                "message": mensaje,
                "response": content,
                "usage": usage,
                "timestamp": datetime.now().isoformat()
            }
            save_conversation_history(conversation)
            
    except APIError as e:
        console.print(f"[red]❌ Error de {e.api_name}: {e.message}[/red]")
        if e.status_code:
            console.print(f"[red]Código de estado: {e.status_code}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('comando')
@click.option('--safe', is_flag=True, help='Ejecutar con validación de seguridad')
@click.option('--timeout', default=30, help='Timeout en segundos')
def execute(comando, safe, timeout):
    """⚡ Ejecuta comandos del sistema de forma segura
    
    Ejecuta comandos con validación de seguridad y whitelist.
    
    Ejemplos:
    \b
    chispart-dev execute "git status" --safe
    chispart-dev execute "ls -la" --safe
    chispart-dev execute "python3 --version" --safe
    """
    if safe:
        # Usar el sistema de seguridad
        validation = security_manager.validate_command(comando)
        
        if not validation.is_allowed:
            console.print(Panel(
                f"[red]❌ Comando no permitido[/red]\n\n"
                f"[yellow]Razón:[/yellow] {validation.reason}\n\n"
                f"[blue]Comando:[/blue] {comando}",
                title="🛡️ Seguridad",
                border_style="red"
            ))
            return
    
    # Ejecutar comando
    console.print(Panel(
        f"[bold green]Ejecutando:[/bold green] {comando}\n"
        f"[dim]Timeout: {timeout}s[/dim]",
        title="⚡ Ejecución de Comando",
        border_style="blue"
    ))
    
    try:
        start_time = time.time()
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            console.print(Panel(
                f"[green]✅ Éxito (código: {result.returncode})[/green]\n"
                f"[dim]Tiempo: {execution_time:.2f}s[/dim]\n\n"
                f"{result.stdout}",
                title="📤 Salida",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]❌ Error (código: {result.returncode})[/red]\n"
                f"[dim]Tiempo: {execution_time:.2f}s[/dim]\n\n"
                f"[red]Error:[/red]\n{result.stderr}\n\n"
                f"[yellow]Salida:[/yellow]\n{result.stdout}",
                title="📤 Resultado",
                border_style="red"
            ))
            
    except subprocess.TimeoutExpired:
        console.print(f"[red]❌ Comando excedió el timeout de {timeout}s[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando comando: {str(e)}[/red]")

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
    security_manager.display_security_status()
    
    if interactive:
        security_manager.interactive_security_config()

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
        f"• 🛡️ Sistema de seguridad robusto\n\n"
        f"[bold yellow]APIs Soportadas:[/bold yellow]\n"
        f"• Chispart (BlackboxAI) - 60+ modelos\n"
        f"• Qwen AI - Modelos especializados\n"
        f"• Google Gemini - Multimodal\n"
        f"• Mistral Codestral - Código\n\n"
        f"[bold blue]Desarrollado por:[/bold blue] Equipo BLACKBOX\n"
        f"[bold magenta]Licencia:[/bold magenta] MIT",
        title="📋 Información del Sistema",
        border_style="blue"
    ))

if __name__ == "__main__":
    cli()
