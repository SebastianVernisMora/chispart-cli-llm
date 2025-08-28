"""
Sistema de Gestión de Equipos de Desarrollo para Chispart CLI
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@dataclass
class TeamMember:
    """Representa un miembro del equipo"""
    name: str
    profile: str  # devops, frontend, backend, etc.
    role: str     # lead, senior, junior, etc.
    specialties: List[str]
    preferred_models: List[str]
    active: bool = True

@dataclass
class DevelopmentTeam:
    """Representa un equipo de desarrollo completo"""
    id: str
    name: str
    description: str
    members: List[TeamMember]
    project_type: str  # web, mobile, api, fullstack, etc.
    tech_stack: List[str]
    preferred_apis: List[str]
    created_at: str
    last_used: str
    active: bool = True
    
    def get_member_count(self) -> int:
        """Obtiene el número de miembros activos"""
        return len([m for m in self.members if m.active])
    
    def get_profiles_summary(self) -> Dict[str, int]:
        """Obtiene resumen de perfiles en el equipo"""
        profiles = {}
        for member in self.members:
            if member.active:
                profiles[member.profile] = profiles.get(member.profile, 0) + 1
        return profiles

class TeamManager:
    """Gestor de equipos de desarrollo"""
    
    def __init__(self):
        self.teams_file = "teams.json"
        self.teams: Dict[str, DevelopmentTeam] = {}
        self.load_teams()
    
    def load_teams(self):
        """Carga los equipos desde archivo"""
        try:
            if os.path.exists(self.teams_file):
                with open(self.teams_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for team_id, team_data in data.items():
                        # Convertir miembros de dict a TeamMember
                        members = []
                        for member_data in team_data.get('members', []):
                            members.append(TeamMember(**member_data))
                        
                        team_data['members'] = members
                        self.teams[team_id] = DevelopmentTeam(**team_data)
        except Exception as e:
            console.print(f"[yellow]Advertencia: Error cargando equipos: {e}[/yellow]")
            self.teams = {}
    
    def save_teams(self):
        """Guarda los equipos en archivo"""
        try:
            # Convertir equipos a formato serializable
            data = {}
            for team_id, team in self.teams.items():
                team_dict = asdict(team)
                data[team_id] = team_dict
            
            with open(self.teams_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]Error guardando equipos: {e}[/red]")
    
    def create_team(self, name: str, description: str, project_type: str, 
                   tech_stack: List[str], preferred_apis: List[str]) -> str:
        """Crea un nuevo equipo"""
        team_id = name.lower().replace(' ', '_').replace('-', '_')
        
        if team_id in self.teams:
            raise ValueError(f"Ya existe un equipo con ID: {team_id}")
        
        team = DevelopmentTeam(
            id=team_id,
            name=name,
            description=description,
            members=[],
            project_type=project_type,
            tech_stack=tech_stack,
            preferred_apis=preferred_apis,
            created_at=datetime.now().isoformat(),
            last_used=datetime.now().isoformat(),
            active=True
        )
        
        self.teams[team_id] = team
        self.save_teams()
        return team_id
    
    def add_member(self, team_id: str, name: str, profile: str, role: str,
                   specialties: List[str], preferred_models: List[str]):
        """Añade un miembro al equipo"""
        if team_id not in self.teams:
            raise ValueError(f"Equipo no encontrado: {team_id}")
        
        member = TeamMember(
            name=name,
            profile=profile,
            role=role,
            specialties=specialties,
            preferred_models=preferred_models,
            active=True
        )
        
        self.teams[team_id].members.append(member)
        self.teams[team_id].last_used = datetime.now().isoformat()
        self.save_teams()
    
    def get_team(self, team_id: str) -> Optional[DevelopmentTeam]:
        """Obtiene un equipo por ID"""
        return self.teams.get(team_id)
    
    def list_teams(self) -> List[DevelopmentTeam]:
        """Lista todos los equipos activos"""
        return [team for team in self.teams.values() if team.active]
    
    def activate_team(self, team_id: str):
        """Activa un equipo para uso"""
        if team_id not in self.teams:
            raise ValueError(f"Equipo no encontrado: {team_id}")
        
        self.teams[team_id].last_used = datetime.now().isoformat()
        self.save_teams()
    
    def delete_team(self, team_id: str):
        """Elimina un equipo"""
        if team_id not in self.teams:
            raise ValueError(f"Equipo no encontrado: {team_id}")
        
        self.teams[team_id].active = False
        self.save_teams()
    
    def get_team_recommendations(self, team_id: str) -> Dict[str, Any]:
        """Obtiene recomendaciones para el equipo"""
        team = self.get_team(team_id)
        if not team:
            return {}
        
        # Modelos recomendados basados en miembros
        recommended_models = set()
        for member in team.members:
            if member.active:
                recommended_models.update(member.preferred_models)
        
        # APIs recomendadas
        recommended_apis = team.preferred_apis
        
        # Herramientas recomendadas por tech stack
        tool_recommendations = self._get_tool_recommendations(team.tech_stack)
        
        return {
            "models": list(recommended_models),
            "apis": recommended_apis,
            "tools": tool_recommendations,
            "profiles_needed": self._analyze_team_balance(team)
        }
    
    def _get_tool_recommendations(self, tech_stack: List[str]) -> List[str]:
        """Obtiene recomendaciones de herramientas basadas en tech stack"""
        tools = []
        
        for tech in tech_stack:
            tech_lower = tech.lower()
            if 'react' in tech_lower or 'vue' in tech_lower or 'angular' in tech_lower:
                tools.extend(['npm', 'yarn', 'webpack', 'vite'])
            elif 'python' in tech_lower:
                tools.extend(['pip', 'poetry', 'pytest', 'black'])
            elif 'node' in tech_lower or 'javascript' in tech_lower:
                tools.extend(['npm', 'node', 'jest', 'eslint'])
            elif 'docker' in tech_lower:
                tools.extend(['docker', 'docker-compose', 'kubectl'])
            elif 'git' in tech_lower:
                tools.extend(['git', 'github', 'gitlab'])
        
        return list(set(tools))
    
    def _analyze_team_balance(self, team: DevelopmentTeam) -> Dict[str, str]:
        """Analiza el balance del equipo y sugiere mejoras"""
        profiles = team.get_profiles_summary()
        suggestions = {}
        
        if team.project_type == 'fullstack':
            if 'frontend' not in profiles:
                suggestions['frontend'] = "Considera añadir un desarrollador frontend"
            if 'backend' not in profiles:
                suggestions['backend'] = "Considera añadir un desarrollador backend"
            if 'devops' not in profiles and team.get_member_count() > 3:
                suggestions['devops'] = "Para equipos grandes, considera añadir DevOps"
        
        elif team.project_type == 'web':
            if 'frontend' not in profiles:
                suggestions['frontend'] = "Proyecto web necesita desarrollador frontend"
            if 'qa' not in profiles and team.get_member_count() > 2:
                suggestions['qa'] = "Considera añadir QA para testing"
        
        return suggestions
    
    def display_teams_table(self):
        """Muestra tabla de equipos"""
        teams = self.list_teams()
        
        if not teams:
            console.print("[yellow]No hay equipos creados[/yellow]")
            return
        
        table = Table(title="🏗️ Equipos de Desarrollo")
        table.add_column("ID", style="cyan")
        table.add_column("Nombre", style="green")
        table.add_column("Tipo", style="blue")
        table.add_column("Miembros", style="yellow")
        table.add_column("Tech Stack", style="magenta")
        table.add_column("Último Uso", style="dim")
        
        for team in teams:
            tech_stack_str = ", ".join(team.tech_stack[:3])
            if len(team.tech_stack) > 3:
                tech_stack_str += f" (+{len(team.tech_stack)-3})"
            
            # Formatear fecha
            try:
                last_used = datetime.fromisoformat(team.last_used)
                last_used_str = last_used.strftime("%Y-%m-%d")
            except:
                last_used_str = "N/A"
            
            table.add_row(
                team.id,
                team.name,
                team.project_type,
                str(team.get_member_count()),
                tech_stack_str,
                last_used_str
            )
        
        console.print(table)
    
    def display_team_details(self, team_id: str):
        """Muestra detalles completos de un equipo"""
        team = self.get_team(team_id)
        if not team:
            console.print(f"[red]Equipo no encontrado: {team_id}[/red]")
            return
        
        # Panel principal
        info = f"""
[bold green]Nombre:[/bold green] {team.name}
[bold blue]Descripción:[/bold blue] {team.description}
[bold yellow]Tipo de Proyecto:[/bold yellow] {team.project_type}
[bold cyan]Miembros Activos:[/bold cyan] {team.get_member_count()}

[bold magenta]Tech Stack:[/bold magenta]
{chr(10).join(f"  • {tech}" for tech in team.tech_stack)}

[bold purple]APIs Preferidas:[/bold purple]
{chr(10).join(f"  • {api}" for api in team.preferred_apis)}
"""
        
        console.print(Panel(info, title=f"🏗️ Equipo: {team.name}", border_style="green"))
        
        # Tabla de miembros
        if team.members:
            members_table = Table(title="👥 Miembros del Equipo")
            members_table.add_column("Nombre", style="cyan")
            members_table.add_column("Perfil", style="green")
            members_table.add_column("Rol", style="yellow")
            members_table.add_column("Especialidades", style="blue")
            members_table.add_column("Estado", style="magenta")
            
            for member in team.members:
                status = "🟢 Activo" if member.active else "🔴 Inactivo"
                specialties_str = ", ".join(member.specialties[:2])
                if len(member.specialties) > 2:
                    specialties_str += f" (+{len(member.specialties)-2})"
                
                members_table.add_row(
                    member.name,
                    member.profile,
                    member.role,
                    specialties_str,
                    status
                )
            
            console.print(members_table)
        
        # Recomendaciones
        recommendations = self.get_team_recommendations(team_id)
        if recommendations.get('profiles_needed'):
            console.print("\n[bold yellow]💡 Sugerencias de Mejora:[/bold yellow]")
            for profile, suggestion in recommendations['profiles_needed'].items():
                console.print(f"  • {suggestion}")

# Instancia global
team_manager = TeamManager()
