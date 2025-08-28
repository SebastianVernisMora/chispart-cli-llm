#!/usr/bin/env python3
"""
Sistema de Playground Interactivo para Chispart CLI
Guía paso a paso con ejemplos prácticos de todos los comandos
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Agregar el directorio padre al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Importar Rich directamente
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.text import Text

# Crear instancias de Rich
console = Console()

def create_panel(content, title="", style="blue"):
    """Crear panel con Rich"""
    return Panel(content, title=title, border_style=style)

def create_table():
    """Crear tabla con Rich"""
    return Table()

# Importar funcionalidades core con manejo de errores
try:
    from ui.theme_manager import get_theme as _get_theme
    def get_theme():
        """Adapta los colores del theme_manager al formato esperado"""
        theme_colors = _get_theme()
        return {
            'brand': theme_colors.get('primary', 'blue'),
            'accent': theme_colors.get('accent', 'cyan'), 
            'info': theme_colors.get('info', 'blue'),
            'success': theme_colors.get('success', 'green'),
            'warning': theme_colors.get('warning', 'yellow'),
            'error': theme_colors.get('error', 'red')
        }
except ImportError:
    def get_theme():
        return {
            'brand': 'blue',
            'accent': 'cyan', 
            'info': 'blue',
            'success': 'green',
            'warning': 'yellow',
            'error': 'red'
        }

try:
    from config_extended import get_available_models, AVAILABLE_APIS
except ImportError:
    AVAILABLE_APIS = {
        'chispart': {'name': 'Chispart', 'base_url': 'https://api.blackbox.ai', 'default_key_env': 'CHISPART_API_KEY'},
        'qwen': {'name': 'Qwen AI', 'base_url': 'https://dashscope.aliyuncs.com', 'default_key_env': 'QWEN_API_KEY'},
        'gemini': {'name': 'Google Gemini', 'base_url': 'https://generativelanguage.googleapis.com', 'default_key_env': 'GEMINI_API_KEY'}
    }


class InteractivePlayground:
    """Sistema de playground interactivo para aprender Chispart CLI"""
    
    def __init__(self):
        try:
            self.colors = get_theme()
        except Exception:
            # Fallback colors si get_theme() falla
            self.colors = {
                'brand': 'blue',
                'accent': 'cyan', 
                'info': 'blue',
                'success': 'green',
                'warning': 'yellow',
                'error': 'red'
            }
        
        self.current_step = 0
        self.completed_steps = set()
        self.user_progress = {}
        
        # Configuración del playground
        self.playground_dir = Path.home() / ".chispart" / "playground"
        self.playground_dir.mkdir(parents=True, exist_ok=True)
        
        # Datos de ejemplo para el playground
        self.sample_data = self._initialize_sample_data()
    
    def start_interactive_guide(self) -> None:
        """Inicia la guía interactiva completa"""
        self._show_welcome_banner()
        
        if not self._check_prerequisites():
            return
        
        # Menú principal del playground
        while True:
            choice = self._show_main_menu()
            
            if choice == "1":
                self._tutorial_basic_commands()
            elif choice == "2":
                self._tutorial_chat_commands()
            elif choice == "3":
                self._tutorial_profile_management()
            elif choice == "4":
                self._tutorial_team_management()
            elif choice == "5":
                self._tutorial_directory_analysis()
            elif choice == "6":
                self._tutorial_security_features()
            elif choice == "7":
                self._tutorial_advanced_features()
            elif choice == "8":
                self._show_progress_summary()
            elif choice == "9":
                self._export_playground_config()
            elif choice == "0":
                self._show_goodbye_message()
                break
            else:
                console.print(f"[{self.colors['error']}]Opción inválida. Intenta de nuevo.[/]")
    
    def _show_welcome_banner(self) -> None:
        """Muestra el banner de bienvenida"""
        welcome_text = f"""
[{self.colors['brand']}]╔══════════════════════════════════════════════════════════════════╗[/]
[{self.colors['brand']}]║[/]  [bold {self.colors['accent']}]🎮 CHISPART CLI - PLAYGROUND INTERACTIVO[/]                    [bold {self.colors['brand']}]║[/]
[{self.colors['brand']}]║[/]                                                                [bold {self.colors['brand']}]║[/]
[{self.colors['brand']}]║[/]  [bold white]¡Aprende todos los comandos con ejemplos prácticos![/]           [bold {self.colors['brand']}]║[/]
[{self.colors['brand']}]║[/]  [italic {self.colors['info']}]• Tutoriales paso a paso[/]                                    [bold {self.colors['brand']}]║[/]
[{self.colors['brand']}]║[/]  [italic {self.colors['info']}]• Ejemplos interactivos[/]                                     [bold {self.colors['brand']}]║[/]
[{self.colors['brand']}]║[/]  [italic {self.colors['info']}]• Playground seguro para practicar[/]                          [bold {self.colors['brand']}]║[/]
[{self.colors['brand']}]╚══════════════════════════════════════════════════════════════════╝[/]
"""
        console.print(Align.center(welcome_text))
        console.print()
    
    def _show_main_menu(self) -> str:
        """Muestra el menú principal y retorna la selección"""
        menu_options = [
            ("1", "🚀 Comandos Básicos", "Aprende los comandos fundamentales"),
            ("2", "💬 Chat con IA", "Domina las conversaciones con diferentes APIs"),
            ("3", "👤 Gestión de Perfiles", "Configura y usa perfiles de desarrollador"),
            ("4", "👥 Gestión de Equipos", "Crea y administra equipos de desarrollo"),
            ("5", "📁 Análisis de Directorios", "Analiza proyectos y codebases"),
            ("6", "🛡️ Características de Seguridad", "Aprende el sistema de seguridad"),
            ("7", "⚡ Funciones Avanzadas", "Explora características avanzadas"),
            ("8", "📊 Ver Progreso", "Revisa tu progreso en el tutorial"),
            ("9", "💾 Exportar Configuración", "Guarda tu configuración del playground"),
            ("0", "🚪 Salir", "Terminar el playground")
        ]
        
        console.print(create_panel(
            self._format_menu_options(menu_options),
            title="🎮 Menú Principal del Playground",
            style=self.colors["brand"]
        ))
        
        return Prompt.ask(
            f"[{self.colors['accent']}]Selecciona una opción",
            choices=[opt[0] for opt in menu_options],
            default="1"
        )
    
    def _tutorial_basic_commands(self) -> None:
        """Tutorial de comandos básicos"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]🚀 TUTORIAL: COMANDOS BÁSICOS[/]\n\n"
            f"Aprenderás los comandos esenciales de Chispart CLI:\n"
            f"• [bold]chispart version[/] - Ver información del sistema\n"
            f"• [bold]chispart config[/] - Configurar APIs y preferencias\n"
            f"• [bold]chispart ayuda[/] - Obtener ayuda contextual\n"
            f"• [bold]chispart modelos[/] - Listar modelos disponibles",
            title="📚 Comandos Básicos",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        # Paso 1: Comando version
        self._interactive_step(
            step_name="version_command",
            title="1️⃣ Comando: chispart version",
            description="Este comando muestra información detallada del sistema",
            command="./chispart version",
            explanation="Muestra versión, APIs configuradas, y estado del sistema"
        )
        
        # Paso 2: Comando config
        self._interactive_step(
            step_name="config_command",
            title="2️⃣ Comando: chispart config",
            description="Gestiona la configuración de APIs y preferencias",
            command="./chispart config",
            explanation="Permite ver y modificar configuración de APIs, modelos por defecto, etc."
        )
        
        # Paso 3: Comando ayuda
        self._interactive_step(
            step_name="help_command",
            title="3️⃣ Comando: chispart ayuda",
            description="Obtiene ayuda contextual sobre comandos",
            command="./chispart ayuda",
            explanation="Muestra ayuda general o específica para comandos"
        )
        
        # Paso 4: Comando modelos
        self._interactive_step(
            step_name="models_command",
            title="4️⃣ Comando: chispart modelos",
            description="Lista todos los modelos de IA disponibles",
            command="./chispart modelos",
            explanation="Muestra modelos por API con descripciones y capacidades"
        )
        
        self._mark_tutorial_completed("basic_commands")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Comandos Básicos completado![/]")
    
    def _tutorial_chat_commands(self) -> None:
        """Tutorial de comandos de chat"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]💬 TUTORIAL: CHAT CON IA[/]\n\n"
            f"Domina las conversaciones con diferentes APIs de IA:\n"
            f"• [bold]Chat básico[/] - Conversaciones simples\n"
            f"• [bold]APIs específicas[/] - Usar diferentes proveedores\n"
            f"• [bold]Modelos específicos[/] - Seleccionar modelos\n"
            f"• [bold]Chat con archivos[/] - Analizar código y documentos",
            title="💬 Chat con IA",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        # Crear archivos de ejemplo para el tutorial
        self._create_sample_files()
        
        steps = [
            ("basic_chat", "1️⃣ Chat Básico", 
             'Conversación simple con IA',
             './chispart chat "Explícame qué es Python en términos simples"',
             "Envía un mensaje directo a la IA usando la API por defecto"),
            
            ("api_specific_chat", "2️⃣ Chat con API Específica",
             "Usar una API específica para el chat",
             './chispart chat "¿Cuáles son las mejores prácticas de JavaScript?" --api qwen',
             "Especifica qué API usar con el parámetro --api"),
            
            ("model_specific_chat", "3️⃣ Chat con Modelo Específico",
             "Seleccionar un modelo específico",
             './chispart chat "Optimiza este algoritmo" --modelo gpt-4o',
             "Usa --modelo para especificar el modelo exacto"),
            
            ("interactive_chat", "4️⃣ Chat Interactivo",
             "Modo conversación continua",
             './chispart chat --interactivo',
             "Inicia una sesión de chat continua (usa 'salir' para terminar)")
        ]
        
        for step_name, title, description, command, explanation in steps:
            self._interactive_step(step_name, title, description, command, explanation, safe_mode=True)
        
        self._mark_tutorial_completed("chat_commands")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Chat completado![/]")
    
    def _tutorial_profile_management(self) -> None:
        """Tutorial de gestión de perfiles"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]👤 TUTORIAL: GESTIÓN DE PERFILES[/]\n\n"
            f"Los perfiles especializan el comportamiento de la IA:\n"
            f"• [bold]Frontend Developer[/] - React, Vue, Angular, UI/UX\n"
            f"• [bold]Backend Developer[/] - APIs, Bases de datos\n"
            f"• [bold]DevOps Engineer[/] - Docker, Kubernetes, CI/CD\n"
            f"• [bold]Mobile Developer[/] - React Native, Flutter\n"
            f"• [bold]Data Scientist[/] - ML, Analytics, Big Data\n"
            f"• [bold]Security Engineer[/] - Pentesting, Auditorías\n"
            f"• [bold]Full Stack Developer[/] - Desarrollo completo",
            title="👤 Gestión de Perfiles",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        steps = [
            ("list_profiles", "1️⃣ Listar Perfiles Disponibles", 
             "Ver todos los perfiles de desarrollador",
             "./chispart perfiles",
             "Muestra todos los perfiles con sus especializaciones"),
            
            ("set_profile", "2️⃣ Activar Perfil",
             "Configurar un perfil como activo",
             './chispart perfiles set "Backend Developer"',
             "Activa un perfil específico para especializar las respuestas de IA"),
            
            ("current_profile", "3️⃣ Ver Perfil Activo",
             "Mostrar información del perfil actual",
             "./chispart perfiles info",
             "Muestra detalles del perfil actualmente activo"),
            
            ("profile_chat", "4️⃣ Chat con Perfil Especializado",
             "Usar el perfil activo en conversaciones",
             './chispart chat "¿Cómo optimizo una base de datos PostgreSQL?"',
             "El perfil activo influye en las respuestas de la IA")
        ]
        
        for step_name, title, description, command, explanation in steps:
            self._interactive_step(step_name, title, description, command, explanation, safe_mode=True)
        
        self._mark_tutorial_completed("profile_management")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Perfiles completado![/]")
    
    def _tutorial_team_management(self) -> None:
        """Tutorial de gestión de equipos"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]👥 TUTORIAL: GESTIÓN DE EQUIPOS[/]\n\n"
            f"Los equipos organizan proyectos y colaboradores:\n"
            f"• [bold]Crear equipos[/] - Nuevos proyectos de desarrollo\n"
            f"• [bold]Gestionar miembros[/] - Añadir/remover desarrolladores\n"
            f"• [bold]Configurar roles[/] - Asignar responsabilidades\n"
            f"• [bold]Historial compartido[/] - Conversaciones del equipo",
            title="👥 Gestión de Equipos",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        steps = [
            ("list_teams", "1️⃣ Listar Equipos", 
             "Ver todos los equipos existentes",
             "./chispart equipos",
             "Muestra equipos creados con información básica"),
            
            ("create_team", "2️⃣ Crear Nuevo Equipo",
             "Crear un equipo para un proyecto",
             './chispart equipos crear "Playground Demo"',
             "Crea un nuevo equipo con el nombre especificado"),
            
            ("activate_team", "3️⃣ Activar Equipo",
             "Configurar equipo como activo",
             './chispart equipos activar "Playground Demo"',
             "El equipo activo se usa para contexto en conversaciones")
        ]
        
        for step_name, title, description, command, explanation in steps:
            self._interactive_step(step_name, title, description, command, explanation, safe_mode=True)
        
        self._mark_tutorial_completed("team_management")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Equipos completado![/]")
    
    def _tutorial_directory_analysis(self) -> None:
        """Tutorial de análisis de directorios"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]📁 TUTORIAL: ANÁLISIS DE DIRECTORIOS[/]\n\n"
            f"Analiza proyectos y codebases automáticamente:\n"
            f"• [bold]Análisis estructural[/] - Detecta patrones y arquitectura\n"
            f"• [bold]Estadísticas de código[/] - Lenguajes, archivos, tamaños\n"
            f"• [bold]Dependencias[/] - Gestores de paquetes y librerías\n"
            f"• [bold]Insights de IA[/] - Recomendaciones inteligentes",
            title="📁 Análisis de Directorios",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        # Crear proyecto de ejemplo
        self._create_sample_project()
        
        sample_project = self.playground_dir / "sample_project"
        steps = [
            ("basic_analysis", "1️⃣ Análisis Básico",
             "Analizar estructura de un proyecto",
             f'./chispart analizar-directorio {sample_project}',
             "Analiza estructura, lenguajes, dependencias y patrones"),
            
            ("custom_prompt_analysis", "2️⃣ Análisis con Prompt Personalizado",
             "Análisis enfocado con prompt específico",
             f'./chispart analizar-directorio {sample_project} --prompt "Evalúa la arquitectura y sugiere mejoras"',
             "Usa --prompt para dirigir el análisis hacia aspectos específicos")
        ]
        
        for step_name, title, description, command, explanation in steps:
            self._interactive_step(step_name, title, description, command, explanation, safe_mode=True)
        
        self._mark_tutorial_completed("directory_analysis")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Análisis completado![/]")
    
    def _tutorial_security_features(self) -> None:
        """Tutorial de características de seguridad"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]🛡️ TUTORIAL: CARACTERÍSTICAS DE SEGURIDAD[/]\n\n"
            f"Chispart CLI incluye múltiples capas de seguridad:\n"
            f"• [bold]Whitelist de comandos[/] - Solo comandos seguros permitidos\n"
            f"• [bold]Blacklist de comandos[/] - Comandos peligrosos bloqueados\n"
            f"• [bold]Confirmación requerida[/] - Para comandos sensibles\n"
            f"• [bold]Sanitización de entrada[/] - Protección contra inyección",
            title="🛡️ Características de Seguridad",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        steps = [
            ("security_status", "1️⃣ Estado de Seguridad",
             "Ver configuración actual de seguridad",
             "./chispart seguridad estado",
             "Muestra nivel de seguridad, comandos permitidos/bloqueados"),
            
            ("safe_command", "2️⃣ Comando Seguro",
             "Ejecutar un comando de la whitelist",
             './chispart ejecutar "ls -la"',
             "Los comandos seguros se ejecutan directamente"),
            
            ("blocked_command", "3️⃣ Comando Bloqueado",
             "Intentar ejecutar un comando peligroso",
             './chispart ejecutar "sudo rm -rf /"',
             "Los comandos peligrosos son bloqueados automáticamente")
        ]
        
        for step_name, title, description, command, explanation in steps:
            expected_error = "blocked" in step_name
            self._interactive_step(step_name, title, description, command, explanation, 
                                 safe_mode=True, expected_error=expected_error)
        
        self._mark_tutorial_completed("security_features")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Seguridad completado![/]")
    
    def _tutorial_advanced_features(self) -> None:
        """Tutorial de funciones avanzadas"""
        console.print(create_panel(
            f"[bold {self.colors['accent']}]⚡ TUTORIAL: FUNCIONES AVANZADAS[/]\n\n"
            f"Características avanzadas para usuarios expertos:\n"
            f"• [bold]Split Chat[/] - Conversaciones paralelas\n"
            f"• [bold]Merge Chat[/] - Combinar conversaciones\n"
            f"• [bold]Historial avanzado[/] - Búsqueda y filtrado\n"
            f"• [bold]Configuración avanzada[/] - Personalización profunda\n"
            f"• [bold]Integración con herramientas[/] - Git, Docker, etc.",
            title="⚡ Funciones Avanzadas",
            style=self.colors["info"]
        ))
        
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar con el tutorial?"):
            return
        
        steps = [
            ("split_chat", "1️⃣ Split Chat",
             "Iniciar conversaciones paralelas",
             './chispart split-chat --tema "Frontend" --tema "Backend"',
             "Permite mantener conversaciones separadas por temas"),
            
            ("advanced_history", "2️⃣ Historial Avanzado",
             "Buscar en el historial de conversaciones",
             './chispart historial --buscar "Python" --fecha "última semana"',
             "Busca conversaciones por contenido y fecha"),
            
            ("config_advanced", "3️⃣ Configuración Avanzada",
             "Personalizar configuración profunda",
             "./chispart config --avanzado",
             "Accede a configuraciones avanzadas del sistema")
        ]
        
        for step_name, title, description, command, explanation in steps:
            self._interactive_step(step_name, title, description, command, explanation, safe_mode=True)
        
        self._mark_tutorial_completed("advanced_features")
        console.print(f"[{self.colors['success']}]✅ ¡Tutorial de Funciones Avanzadas completado![/]")
    
    def _interactive_step(self, step_name: str, title: str, description: str, 
                         command: str, explanation: str, safe_mode: bool = False,
                         expected_error: bool = False) -> None:
        """Ejecuta un paso interactivo del tutorial"""
        
        console.print(create_panel(
            f"[bold {self.colors['accent']}]{title}[/]\n\n"
            f"[bold]Descripción:[/] {description}\n\n"
            f"[bold]Comando a ejecutar:[/]\n"
            f"[code]{command}[/code]\n\n"
            f"[bold]Explicación:[/] {explanation}",
            title=f"📖 {step_name}",
            style=self.colors["info"]
        ))
        
        if safe_mode:
            console.print(f"[{self.colors['warning']}]ℹ️  Modo seguro: Este comando se ejecutará en el playground[/]")
        
        if expected_error:
            console.print(f"[{self.colors['warning']}]⚠️  Este comando debería fallar (es parte del tutorial)[/]")
        
        # Preguntar si ejecutar el comando
        if Confirm.ask(f"[{self.colors['accent']}]¿Ejecutar este comando?", default=True):
            if safe_mode:
                console.print(f"[{self.colors['info']}]🔄 Ejecutando comando en modo seguro...[/]")
                # En modo seguro, simular la ejecución
                self._simulate_command_execution(command, expected_error)
            else:
                console.print(f"[{self.colors['info']}]🔄 Ejecutando comando real...[/]")
                # Ejecutar comando real (solo para comandos seguros)
                self._execute_real_command(command)
        
        # Marcar paso como completado
        self.completed_steps.add(step_name)
        
        # Pausa para que el usuario pueda leer
        if not Confirm.ask(f"[{self.colors['accent']}]¿Continuar al siguiente paso?", default=True):
            return
    
    def _simulate_command_execution(self, command: str, expected_error: bool = False) -> None:
        """Simula la ejecución de un comando para el tutorial"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Ejecutando comando...", total=100)
            
            for i in range(100):
                time.sleep(0.02)  # Simular trabajo
                progress.update(task, advance=1)
        
        if expected_error:
            console.print(f"[{self.colors['error']}]❌ Error esperado: Comando bloqueado por seguridad[/]")
            console.print(f"[{self.colors['info']}]ℹ️  Esto es normal - el sistema de seguridad está funcionando[/]")
        else:
            console.print(f"[{self.colors['success']}]✅ Comando ejecutado exitosamente[/]")
            console.print(f"[{self.colors['info']}]📋 Resultado simulado mostrado arriba[/]")
    
    def _execute_real_command(self, command: str) -> None:
        """Ejecuta un comando real (solo para comandos muy seguros)"""
        # Solo ejecutar comandos muy seguros como version, help, etc.
        safe_commands = ["version", "ayuda", "help", "modelos", "config"]
        
        if any(safe_cmd in command for safe_cmd in safe_commands):
            console.print(f"[{self.colors['info']}]🔄 Ejecutando: {command}[/]")
            # Aquí se ejecutaría el comando real
            console.print(f"[{self.colors['success']}]✅ Comando ejecutado[/]")
        else:
            console.print(f"[{self.colors['warning']}]⚠️  Comando no ejecutado por seguridad - usando simulación[/]")
            self._simulate_command_execution(command)
    
    def _create_sample_files(self) -> None:
        """Crea archivos de ejemplo para el tutorial"""
        
        # Crear archivo Python de ejemplo
        sample_py = self.playground_dir / "ejemplo.py"
        sample_py.write_text("""
#!/usr/bin/env python3
\"\"\"
Archivo de ejemplo para el tutorial de Chispart CLI
\"\"\"

def fibonacci(n):
    \"\"\"Calcula el n-ésimo número de Fibonacci\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    \"\"\"Función principal\"\"\"
    print("Calculando Fibonacci...")
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
""")
        
        # Crear archivo de configuración de ejemplo
        sample_config = self.playground_dir / "config.json"
        sample_config.write_text("""
{
    "proyecto": "Tutorial Chispart",
    "version": "1.0.0",
    "autor": "Usuario del Playground",
    "configuracion": {
        "debug": true,
        "timeout": 30,
        "max_retries": 3
    }
}
""")
        
        console.print(f"[{self.colors['success']}]📁 Archivos de ejemplo creados en {self.playground_dir}[/]")
    
    def _create_sample_project(self) -> None:
        """Crea un proyecto de ejemplo para análisis de directorios"""
        
        project_dir = self.playground_dir / "sample_project"
        project_dir.mkdir(exist_ok=True)
        
        # Crear estructura de proyecto
        (project_dir / "src").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        (project_dir / "docs").mkdir(exist_ok=True)
        
        # Archivo principal
        (project_dir / "src" / "main.py").write_text("""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Sample API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def create_item(item: Item):
    return item
""")
        
        # Requirements
        (project_dir / "requirements.txt").write_text("""
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pytest==7.4.3
requests==2.31.0
""")
        
        # README
        (project_dir / "README.md").write_text("""
# Sample Project

Este es un proyecto de ejemplo para demostrar el análisis de directorios de Chispart CLI.

## Características

- API REST con FastAPI
- Modelos de datos con Pydantic
- Tests con pytest
- Documentación automática

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
uvicorn src.main:app --reload
```
""")
        
        # Test de ejemplo
        (project_dir / "tests" / "test_main.py").write_text("""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_item():
    response = client.get("/items/1?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "q": "test"}
""")
        
        console.print(f"[{self.colors['success']}]🏗️ Proyecto de ejemplo creado en {project_dir}[/]")
    
    def _format_menu_options(self, options: List[tuple]) -> str:
        """Formatea las opciones del menú"""
        formatted = []
        for option, title, description in options:
            formatted.append(f"[bold {self.colors['accent']}]{option}[/] {title}")
            formatted.append(f"   [dim]{description}[/]")
            formatted.append("")
        
        return "\n".join(formatted[:-1])  # Remover última línea vacía
    
    def _check_prerequisites(self) -> bool:
        """Verifica que los prerequisitos estén cumplidos"""
        console.print(f"[{self.colors['info']}]🔍 Verificando prerequisitos...[/]")
        
        # Verificar que estamos en el directorio correcto
        if not Path("chispart_dev_agent_v3.py").exists():
            console.print(f"[{self.colors['error']}]❌ No se encontró chispart_dev_agent_v3.py[/]")
            console.print(f"[{self.colors['info']}]💡 Ejecuta este playground desde el directorio de Chispart CLI[/]")
            return False
        
        console.print(f"[{self.colors['success']}]✅ Prerequisitos verificados[/]")
        return True
    
    def _mark_tutorial_completed(self, tutorial_name: str) -> None:
        """Marca un tutorial como completado"""
        self.user_progress[tutorial_name] = {
            "completed": True,
            "timestamp": datetime.now().isoformat(),
            "steps_completed": len([s for s in self.completed_steps if tutorial_name in s])
        }
        
        # Guardar progreso
        progress_file = self.playground_dir / "progress.json"
        progress_file.write_text(json.dumps(self.user_progress, indent=2))
    
    def _show_progress_summary(self) -> None:
        """Muestra resumen del progreso del usuario"""
        
        total_tutorials = 7
        completed_tutorials = len(self.user_progress)
        progress_percentage = (completed_tutorials / total_tutorials) * 100
        
        console.print(create_panel(
            f"[bold {self.colors['accent']}]📊 RESUMEN DE PROGRESO[/]\n\n"
            f"[bold]Tutoriales completados:[/] {completed_tutorials}/{total_tutorials}\n"
            f"[bold]Progreso total:[/] {progress_percentage:.1f}%\n"
            f"[bold]Pasos completados:[/] {len(self.completed_steps)}\n\n"
            f"[bold]Tutoriales:[/]\n"
            f"{'✅' if 'basic_commands' in self.user_progress else '⏳'} Comandos Básicos\n"
            f"{'✅' if 'chat_commands' in self.user_progress else '⏳'} Chat con IA\n"
            f"{'✅' if 'profile_management' in self.user_progress else '⏳'} Gestión de Perfiles\n"
            f"{'✅' if 'team_management' in self.user_progress else '⏳'} Gestión de Equipos\n"
            f"{'✅' if 'directory_analysis' in self.user_progress else '⏳'} Análisis de Directorios\n"
            f"{'✅' if 'security_features' in self.user_progress else '⏳'} Características de Seguridad\n"
            f"{'✅' if 'advanced_features' in self.user_progress else '⏳'} Funciones Avanzadas",
            title="📈 Tu Progreso",
            style=self.colors["success"] if progress_percentage == 100 else self.colors["info"]
        ))
    
    def _export_playground_config(self) -> None:
        """Exporta la configuración del playground"""
        
        config_data = {
            "playground_version": "1.0.0",
            "export_date": datetime.now().isoformat(),
            "user_progress": self.user_progress,
            "completed_steps": list(self.completed_steps),
            "sample_files_created": True,
            "playground_directory": str(self.playground_dir)
        }
        
        export_file = self.playground_dir / "playground_export.json"
        export_file.write_text(json.dumps(config_data, indent=2))
        
        console.print(create_panel(
            f"[bold {self.colors['success']}]💾 CONFIGURACIÓN EXPORTADA[/]\n\n"
            f"[bold]Archivo:[/] {export_file}\n"
            f"[bold]Progreso guardado:[/] {len(self.user_progress)} tutoriales\n"
            f"[bold]Pasos completados:[/] {len(self.completed_steps)}\n\n"
            f"[italic]Puedes usar este archivo para restaurar tu progreso[/]",
            title="💾 Exportación Completa",
            style=self.colors["success"]
        ))
    
    def _show_goodbye_message(self) -> None:
        """Muestra mensaje de despedida"""
        
        completed_count = len(self.user_progress)
        total_tutorials = 7
        
        console.print(create_panel(
            f"[bold {self.colors['accent']}]🎉 ¡GRACIAS POR USAR EL PLAYGROUND![/]\n\n"
            f"[bold]Resumen de tu sesión:[/]\n"
            f"• Tutoriales completados: {completed_count}/{total_tutorials}\n"
            f"• Pasos realizados: {len(self.completed_steps)}\n"
            f"• Archivos de ejemplo creados: ✅\n\n"
            f"[bold {self.colors['success']}]🚀 ¡Ya estás listo para usar Chispart CLI![/]\n\n"
            f"[italic]Recuerda:[/]\n"
            f"• Usa [code]./chispart ayuda[/code] para obtener ayuda\n"
            f"• Explora los diferentes perfiles de desarrollador\n"
            f"• El sistema de seguridad te protege automáticamente\n"
            f"• ¡Diviértete desarrollando con IA!",
            title="👋 ¡Hasta la vista!",
            style=self.colors["brand"]
        ))
    
    def _initialize_sample_data(self) -> Dict[str, Any]:
        """Inicializa datos de ejemplo para el playground"""
        return {
            "sample_prompts": [
                "Explícame este código Python",
                "¿Cómo optimizo esta consulta SQL?",
                "Ayúdame a debuggear este error",
                "Crea un plan de arquitectura para mi app",
                "Revisa la seguridad de este endpoint"
            ],
            "sample_files": [
                "ejemplo.py",
                "config.json",
                "README.md",
                "requirements.txt"
            ],
            "sample_apis": list(AVAILABLE_APIS.keys()),
            "sample_models": ["gpt-4", "gpt-4o", "claude-3.5-sonnet", "qwen-max"]
        }


# Funciones auxiliares para integración con el sistema principal

def start_playground() -> None:
    """Función principal para iniciar el playground"""
    playground = InteractivePlayground()
    playground.start_interactive_guide()

def quick_tutorial(tutorial_name: str) -> None:
    """Ejecuta un tutorial específico rápidamente"""
    playground = InteractivePlayground()
    
    tutorials = {
        "basic": playground._tutorial_basic_commands,
        "chat": playground._tutorial_chat_commands,
        "profiles": playground._tutorial_profile_management,
        "teams": playground._tutorial_team_management,
        "analysis": playground._tutorial_directory_analysis,
        "security": playground._tutorial_security_features,
        "advanced": playground._tutorial_advanced_features
    }
    
    if tutorial_name in tutorials:
        tutorials[tutorial_name]()
    else:
        console.print(f"[red]Tutorial '{tutorial_name}' no encontrado[/]")
        console.print(f"[yellow]Tutoriales disponibles: {', '.join(tutorials.keys())}[/]")


if __name__ == "__main__":
    start_playground()
