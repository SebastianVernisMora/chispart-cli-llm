"""
ATC Agent - Asistente Técnico Chispart
Agente experto interno para soporte y resolución de problemas
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class ATCSession:
    """Sesión de soporte ATC"""
    id: str
    issue_type: str
    description: str
    status: str  # active, resolved, escalated
    steps_taken: List[str]
    diagnostics: Dict[str, Any]
    created_at: str
    resolved_at: Optional[str] = None

class ATCAgent:
    """Agente de Asistencia Técnica Chispart"""
    
    def __init__(self):
        self.sessions_file = "atc_sessions.json"
        self.active_session: Optional[ATCSession] = None
        self.knowledge_base = self._load_knowledge_base()
        self.diagnostic_commands = self._get_diagnostic_commands()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Carga la base de conocimientos de ATC"""
        return {
            "common_issues": {
                "api_connection": {
                    "symptoms": ["timeout", "connection error", "api error", "no response"],
                    "solutions": [
                        "Verificar clave API en .env",
                        "Comprobar conexión a internet",
                        "Verificar formato de clave API",
                        "Probar con API diferente"
                    ],
                    "diagnostics": ["ping google.com", "curl -I https://api.blackbox.ai"]
                },
                "import_error": {
                    "symptoms": ["modulenotfounderror", "import error", "no module named"],
                    "solutions": [
                        "Instalar dependencias faltantes",
                        "Verificar entorno virtual",
                        "Actualizar pip",
                        "Reinstalar paquetes"
                    ],
                    "diagnostics": ["pip list", "python -c 'import sys; print(sys.path)'"]
                },
                "permission_error": {
                    "symptoms": ["permission denied", "access denied", "not allowed"],
                    "solutions": [
                        "Verificar permisos de archivo",
                        "Ejecutar sin sudo (por seguridad)",
                        "Cambiar propietario de archivos",
                        "Verificar configuración de seguridad"
                    ],
                    "diagnostics": ["ls -la", "whoami", "pwd"]
                },
                "command_blocked": {
                    "symptoms": ["comando no permitido", "blocked command", "whitelist"],
                    "solutions": [
                        "Usar comando alternativo de la whitelist",
                        "Verificar configuración de seguridad",
                        "Ejecutar comando manualmente fuera del sistema",
                        "Solicitar añadir comando a whitelist"
                    ],
                    "diagnostics": ["python3 chispart_dev_agent.py security"]
                },
                "model_error": {
                    "symptoms": ["model not available", "invalid model", "modelo no disponible"],
                    "solutions": [
                        "Verificar modelos disponibles",
                        "Usar modelo por defecto",
                        "Cambiar API provider",
                        "Verificar configuración de API"
                    ],
                    "diagnostics": ["python3 chispart_dev_agent.py modelos"]
                }
            },
            "installation_issues": {
                "dependency_conflicts": [
                    "Crear entorno virtual limpio",
                    "Actualizar pip a última versión",
                    "Instalar dependencias una por una",
                    "Verificar versiones de Python"
                ],
                "termux_specific": [
                    "Actualizar paquetes Termux: pkg update && pkg upgrade",
                    "Instalar dependencias de compilación: pkg install clang make cmake",
                    "Configurar almacenamiento: termux-setup-storage",
                    "Verificar espacio disponible"
                ]
            },
            "performance_issues": {
                "slow_responses": [
                    "Verificar conexión de red",
                    "Cambiar a modelo más rápido",
                    "Reducir tamaño de contexto",
                    "Usar API con mejor latencia"
                ],
                "memory_issues": [
                    "Cerrar aplicaciones innecesarias",
                    "Usar modelos más pequeños",
                    "Limpiar caché del sistema",
                    "Verificar espacio en disco"
                ]
            }
        }
    
    def _get_diagnostic_commands(self) -> Dict[str, List[str]]:
        """Comandos de diagnóstico seguros"""
        return {
            "system": [
                "python3 --version",
                "pip --version", 
                "pwd",
                "whoami",
                "df -h",
                "free -h"
            ],
            "chispart": [
                "python3 chispart_dev_agent.py --help",
                "python3 chispart_dev_agent.py version",
                "python3 chispart_dev_agent.py security",
                "python3 chispart_dev_agent.py modelos"
            ],
            "network": [
                "ping -c 3 google.com",
                "curl -I https://api.blackbox.ai",
                "nslookup google.com"
            ],
            "files": [
                "ls -la",
                "ls -la core/",
                "cat .env | head -1",
                "find . -name '*.py' | head -5"
            ]
        }
    
    def start_support_session(self, issue_description: str) -> str:
        """Inicia una nueva sesión de soporte"""
        session_id = f"atc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analizar tipo de problema
        issue_type = self._classify_issue(issue_description)
        
        session = ATCSession(
            id=session_id,
            issue_type=issue_type,
            description=issue_description,
            status="active",
            steps_taken=[],
            diagnostics={},
            created_at=datetime.now().isoformat()
        )
        
        self.active_session = session
        self._save_session(session)
        
        console.print(Panel(
            f"[bold green]🔧 Sesión de Soporte ATC Iniciada[/bold green]\n\n"
            f"[bold cyan]ID de Sesión:[/bold cyan] {session_id}\n"
            f"[bold yellow]Tipo de Problema:[/bold yellow] {issue_type}\n"
            f"[bold blue]Descripción:[/bold blue] {issue_description}\n\n"
            f"[dim]Iniciando diagnóstico automático...[/dim]",
            title="🚨 ATC - Asistencia Técnica Chispart",
            border_style="green"
        ))
        
        return session_id
    
    def _classify_issue(self, description: str) -> str:
        """Clasifica el tipo de problema basado en la descripción"""
        description_lower = description.lower()
        
        for issue_type, data in self.knowledge_base["common_issues"].items():
            for symptom in data["symptoms"]:
                if symptom in description_lower:
                    return issue_type
        
        return "general"
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Ejecuta diagnósticos automáticos"""
        if not self.active_session:
            return {}
        
        console.print("[bold blue]🔍 Ejecutando Diagnósticos Automáticos...[/bold blue]")
        
        diagnostics = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Diagnósticos del sistema
            task1 = progress.add_task("Verificando sistema...", total=None)
            diagnostics["system"] = self._run_command_group("system")
            progress.update(task1, completed=True)
            
            # Diagnósticos de Chispart
            task2 = progress.add_task("Verificando Chispart...", total=None)
            diagnostics["chispart"] = self._run_command_group("chispart")
            progress.update(task2, completed=True)
            
            # Diagnósticos de red (si es problema de API)
            if self.active_session.issue_type == "api_connection":
                task3 = progress.add_task("Verificando conectividad...", total=None)
                diagnostics["network"] = self._run_command_group("network")
                progress.update(task3, completed=True)
            
            # Diagnósticos de archivos
            task4 = progress.add_task("Verificando archivos...", total=None)
            diagnostics["files"] = self._run_command_group("files")
            progress.update(task4, completed=True)
        
        self.active_session.diagnostics = diagnostics
        self._save_session(self.active_session)
        
        return diagnostics
    
    def _run_command_group(self, group: str) -> Dict[str, Any]:
        """Ejecuta un grupo de comandos de diagnóstico"""
        results = {}
        commands = self.diagnostic_commands.get(group, [])
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=os.getcwd()
                )
                results[cmd] = {
                    "success": result.returncode == 0,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip()
                }
            except Exception as e:
                results[cmd] = {
                    "success": False,
                    "output": "",
                    "error": str(e)
                }
        
        return results
    
    def analyze_and_suggest(self) -> List[str]:
        """Analiza diagnósticos y sugiere soluciones"""
        if not self.active_session or not self.active_session.diagnostics:
            return []
        
        suggestions = []
        issue_type = self.active_session.issue_type
        
        # Sugerencias basadas en tipo de problema
        if issue_type in self.knowledge_base["common_issues"]:
            base_solutions = self.knowledge_base["common_issues"][issue_type]["solutions"]
            suggestions.extend(base_solutions)
        
        # Análisis específico de diagnósticos
        diagnostics = self.active_session.diagnostics
        
        # Verificar problemas de Python/pip
        if "system" in diagnostics:
            python_cmd = next((cmd for cmd in diagnostics["system"] if "python3 --version" in cmd), None)
            if python_cmd and not diagnostics["system"][python_cmd]["success"]:
                suggestions.append("❌ Python3 no está instalado o no funciona correctamente")
        
        # Verificar problemas de Chispart
        if "chispart" in diagnostics:
            help_cmd = next((cmd for cmd in diagnostics["chispart"] if "--help" in cmd), None)
            if help_cmd and not diagnostics["chispart"][help_cmd]["success"]:
                suggestions.append("❌ Chispart CLI no se ejecuta correctamente - verificar instalación")
        
        # Verificar problemas de red
        if "network" in diagnostics:
            ping_cmd = next((cmd for cmd in diagnostics["network"] if "ping" in cmd), None)
            if ping_cmd and not diagnostics["network"][ping_cmd]["success"]:
                suggestions.append("❌ Problemas de conectividad - verificar conexión a internet")
        
        return suggestions
    
    def interactive_troubleshooting(self):
        """Proceso interactivo de resolución de problemas"""
        if not self.active_session:
            console.print("[red]No hay sesión activa[/red]")
            return
        
        console.print(f"\n[bold green]🔧 Resolución Interactiva - Sesión {self.active_session.id}[/bold green]")
        
        # Ejecutar diagnósticos
        self.run_diagnostics()
        
        # Analizar y sugerir
        suggestions = self.analyze_and_suggest()
        
        if suggestions:
            console.print("\n[bold yellow]💡 Sugerencias de Solución:[/bold yellow]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  {i}. {suggestion}")
            
            # Proceso interactivo
            while self.active_session.status == "active":
                console.print("\n[bold cyan]¿Qué te gustaría hacer?[/bold cyan]")
                console.print("1. Probar una solución sugerida")
                console.print("2. Ejecutar comando de diagnóstico específico")
                console.print("3. Obtener más información sobre el problema")
                console.print("4. Marcar como resuelto")
                console.print("5. Escalar a soporte avanzado")
                console.print("6. Salir")
                
                choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6"])
                
                if choice == "1":
                    self._try_suggested_solution(suggestions)
                elif choice == "2":
                    self._run_custom_diagnostic()
                elif choice == "3":
                    self._show_detailed_info()
                elif choice == "4":
                    self._mark_resolved()
                    break
                elif choice == "5":
                    self._escalate_support()
                    break
                elif choice == "6":
                    break
        else:
            console.print("[yellow]No se encontraron sugerencias específicas. Iniciando diagnóstico manual...[/yellow]")
            self._manual_troubleshooting()
    
    def _try_suggested_solution(self, suggestions: List[str]):
        """Permite al usuario probar una solución sugerida"""
        console.print("\n[bold green]Soluciones Disponibles:[/bold green]")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"  {i}. {suggestion}")
        
        try:
            choice = int(Prompt.ask("¿Qué solución quieres probar?", default="1"))
            if 1 <= choice <= len(suggestions):
                selected_solution = suggestions[choice - 1]
                console.print(f"\n[bold blue]Probando:[/bold blue] {selected_solution}")
                
                # Registrar paso
                self.active_session.steps_taken.append(f"Probó solución: {selected_solution}")
                self._save_session(self.active_session)
                
                # Preguntar si funcionó
                if Confirm.ask("¿Esta solución resolvió el problema?"):
                    self._mark_resolved()
                else:
                    console.print("[yellow]Continuando con otras opciones...[/yellow]")
        except ValueError:
            console.print("[red]Opción inválida[/red]")
    
    def _run_custom_diagnostic(self):
        """Ejecuta un comando de diagnóstico personalizado"""
        console.print("\n[bold blue]Comandos de Diagnóstico Disponibles:[/bold blue]")
        
        all_commands = []
        for group, commands in self.diagnostic_commands.items():
            console.print(f"\n[bold cyan]{group.title()}:[/bold cyan]")
            for cmd in commands:
                all_commands.append(cmd)
                console.print(f"  {len(all_commands)}. {cmd}")
        
        try:
            choice = int(Prompt.ask("¿Qué comando quieres ejecutar?", default="1"))
            if 1 <= choice <= len(all_commands):
                cmd = all_commands[choice - 1]
                console.print(f"\n[bold green]Ejecutando:[/bold green] {cmd}")
                
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    console.print(f"[green]✅ Éxito:[/green]\n{result.stdout}")
                else:
                    console.print(f"[red]❌ Error:[/red]\n{result.stderr}")
                
                # Registrar paso
                self.active_session.steps_taken.append(f"Ejecutó diagnóstico: {cmd}")
                self._save_session(self.active_session)
                
        except (ValueError, subprocess.TimeoutExpired) as e:
            console.print(f"[red]Error ejecutando comando: {e}[/red]")
    
    def _show_detailed_info(self):
        """Muestra información detallada sobre el problema"""
        issue_type = self.active_session.issue_type
        
        if issue_type in self.knowledge_base["common_issues"]:
            info = self.knowledge_base["common_issues"][issue_type]
            
            console.print(Panel(
                f"[bold yellow]Síntomas Comunes:[/bold yellow]\n"
                f"{chr(10).join(f'• {s}' for s in info['symptoms'])}\n\n"
                f"[bold green]Soluciones Recomendadas:[/bold green]\n"
                f"{chr(10).join(f'• {s}' for s in info['solutions'])}",
                title=f"📚 Información: {issue_type}",
                border_style="blue"
            ))
    
    def _mark_resolved(self):
        """Marca la sesión como resuelta"""
        self.active_session.status = "resolved"
        self.active_session.resolved_at = datetime.now().isoformat()
        self._save_session(self.active_session)
        
        console.print(Panel(
            "[bold green]✅ Problema Marcado como Resuelto[/bold green]\n\n"
            f"Sesión: {self.active_session.id}\n"
            f"Pasos realizados: {len(self.active_session.steps_taken)}\n"
            f"Tiempo total: {self._calculate_session_duration()}",
            title="🎉 Resolución Exitosa",
            border_style="green"
        ))
    
    def _escalate_support(self):
        """Escala el problema a soporte avanzado"""
        self.active_session.status = "escalated"
        self._save_session(self.active_session)
        
        console.print(Panel(
            "[bold yellow]⬆️ Problema Escalado a Soporte Avanzado[/bold yellow]\n\n"
            f"ID de Sesión: {self.active_session.id}\n"
            f"Tipo: {self.active_session.issue_type}\n"
            f"Descripción: {self.active_session.description}\n\n"
            "[dim]Un especialista revisará tu caso y te contactará.[/dim]",
            title="📞 Escalación de Soporte",
            border_style="yellow"
        ))
    
    def _manual_troubleshooting(self):
        """Proceso manual de resolución de problemas"""
        console.print("\n[bold blue]🔧 Diagnóstico Manual[/bold blue]")
        console.print("Vamos paso a paso para identificar el problema...")
        
        # Serie de preguntas diagnósticas
        questions = [
            "¿El problema ocurre al ejecutar un comando específico?",
            "¿Has modificado algún archivo de configuración recientemente?",
            "¿El problema comenzó después de una instalación o actualización?",
            "¿Tienes conexión a internet estable?",
            "¿Has reiniciado la aplicación desde que comenzó el problema?"
        ]
        
        answers = {}
        for question in questions:
            answer = Confirm.ask(question)
            answers[question] = answer
            self.active_session.steps_taken.append(f"Pregunta: {question} - Respuesta: {answer}")
        
        # Análisis de respuestas
        if answers.get("¿El problema ocurre al ejecutar un comando específico?"):
            console.print("[yellow]💡 Sugerencia: Verifica que el comando esté en la whitelist de seguridad[/yellow]")
        
        if answers.get("¿Has modificado algún archivo de configuración recientemente?"):
            console.print("[yellow]💡 Sugerencia: Revisa los cambios en .env y archivos de configuración[/yellow]")
        
        self._save_session(self.active_session)
    
    def _calculate_session_duration(self) -> str:
        """Calcula la duración de la sesión"""
        if not self.active_session.resolved_at:
            return "En progreso"
        
        try:
            start = datetime.fromisoformat(self.active_session.created_at)
            end = datetime.fromisoformat(self.active_session.resolved_at)
            duration = end - start
            
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutos"
        except:
            return "N/A"
    
    def _save_session(self, session: ATCSession):
        """Guarda la sesión en archivo"""
        try:
            sessions = {}
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    sessions = json.load(f)
            
            sessions[session.id] = {
                "id": session.id,
                "issue_type": session.issue_type,
                "description": session.description,
                "status": session.status,
                "steps_taken": session.steps_taken,
                "diagnostics": session.diagnostics,
                "created_at": session.created_at,
                "resolved_at": session.resolved_at
            }
            
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error guardando sesión: {e}[/red]")
    
    def show_help_guide(self):
        """Muestra la guía de ayuda completa"""
        console.print(Panel(
            """[bold green]🚀 Guía de Ayuda - Chispart Dev Agent[/bold green]

[bold cyan]Comandos Principales:[/bold cyan]
• [bold]chat[/bold] - Conversar con IA usando perfiles especializados
• [bold]execute[/bold] - Ejecutar comandos del sistema de forma segura
• [bold]perfiles[/bold] - Gestionar perfiles de desarrollo
• [bold]modelos[/bold] - Ver modelos de IA disponibles
• [bold]equipos[/bold] - Gestionar equipos de desarrollo
• [bold]split-chat[/bold] - Crear sesiones de chat paralelas
• [bold]security[/bold] - Ver configuración de seguridad
• [bold]ayuda[/bold] - Iniciar asistencia técnica ATC

[bold yellow]Problemas Comunes:[/bold yellow]
• [bold]Error de API:[/bold] Verificar clave en .env
• [bold]Comando bloqueado:[/bold] Usar comando de whitelist
• [bold]Import error:[/bold] Instalar dependencias faltantes
• [bold]Permisos:[/bold] No usar sudo, verificar permisos

[bold magenta]Soporte ATC:[/bold magenta]
• [bold]ayuda "descripción del problema"[/bold] - Iniciar sesión de soporte
• [bold]ayuda --interactivo[/bold] - Diagnóstico paso a paso
• [bold]ayuda --diagnostico[/bold] - Solo ejecutar diagnósticos

[bold blue]Ejemplos de Uso:[/bold blue]
• chispart-dev chat "Crea una API" --profile backend
• chispart-dev execute "git status" --safe
• chispart-dev ayuda "No puedo conectar con la API"
""",
            title="📚 Ayuda - Chispart Dev Agent",
            border_style="blue"
        ))

# Instancia global
atc_agent = ATCAgent()
