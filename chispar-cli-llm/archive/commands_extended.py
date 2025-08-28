"""
Comandos extendidos para Chispart Dev Agent
Incluye comandos para equipos y asistencia técnica ATC
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from config_extended import AVAILABLE_APIS
from core.team_manager import team_manager
from core.atc_agent import atc_agent
from core.dev_profiles import profile_manager

console = Console()

@click.command()
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


@click.command()
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
