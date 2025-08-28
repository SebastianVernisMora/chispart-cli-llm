"""
Componentes interactivos modernos para Chispart CLI
"""

import time
from typing import List, Dict, Any, Optional, Callable
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

from .components import console, create_panel, create_table
from .theme_manager import get_theme

class InteractivePrompt:
    """Prompts interactivos con tema aplicado"""
    
    @staticmethod
    def ask(prompt: str, default: Optional[str] = None, password: bool = False) -> str:
        """Prompt de texto con tema"""
        colors = get_theme()
        styled_prompt = f"[{colors['primary']}]{prompt}[/]"
        return Prompt.ask(styled_prompt, default=default, password=password, console=console.console)
    
    @staticmethod
    def confirm(prompt: str, default: bool = True) -> bool:
        """Prompt de confirmación con tema"""
        colors = get_theme()
        styled_prompt = f"[{colors['accent']}]{prompt}[/]"
        return Confirm.ask(styled_prompt, default=default, console=console.console)
    
    @staticmethod
    def integer(prompt: str, default: Optional[int] = None, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """Prompt de entero con tema"""
        colors = get_theme()
        styled_prompt = f"[{colors['info']}]{prompt}[/]"
        return IntPrompt.ask(styled_prompt, default=default, console=console.console)

class MenuSelector:
    """Selector de menú interactivo"""
    
    def __init__(self, title: str, options: Dict[str, str], description: Optional[str] = None):
        self.title = title
        self.options = options
        self.description = description
        self.colors = get_theme()
    
    def show(self) -> str:
        """Muestra el menú y retorna la opción seleccionada"""
        # Crear tabla de opciones
        table = create_table(title=self.title, show_lines=True)
        table.add_column("Opción", style="chispart.brand", width=10)
        table.add_column("Descripción", style="chispart.dim")
        
        option_keys = list(self.options.keys())
        for i, (key, description) in enumerate(self.options.items(), 1):
            table.add_row(f"{i}. {key}", description)
        
        console.print(table)
        
        if self.description:
            console.print(f"\n[{self.colors['dim']}]{self.description}[/]")
        
        # Prompt para selección
        while True:
            try:
                choice = InteractivePrompt.integer(
                    f"Selecciona una opción (1-{len(option_keys)})",
                    min_value=1,
                    max_value=len(option_keys)
                )
                return option_keys[choice - 1]
            except (ValueError, IndexError):
                console.print(f"[{self.colors['error']}]❌ Opción inválida. Intenta de nuevo.[/]")

class ProgressTracker:
    """Tracker de progreso avanzado"""
    
    def __init__(self, title: str = "Procesando..."):
        self.title = title
        self.colors = get_theme()
        self.progress = Progress(
            SpinnerColumn(style=self.colors["primary"]),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(style=self.colors["primary"], complete_style=self.colors["success"]),
            TaskProgressColumn(),
            console=console.console
        )
        self.tasks = {}
    
    def add_task(self, name: str, total: Optional[int] = None) -> int:
        """Añade una nueva tarea al tracker"""
        task_id = self.progress.add_task(name, total=total)
        self.tasks[name] = task_id
        return task_id
    
    def update(self, task_name: str, advance: int = 1, description: Optional[str] = None):
        """Actualiza el progreso de una tarea"""
        if task_name in self.tasks:
            task_id = self.tasks[task_name]
            self.progress.update(task_id, advance=advance, description=description or task_name)
    
    def complete(self, task_name: str):
        """Marca una tarea como completada"""
        if task_name in self.tasks:
            task_id = self.tasks[task_name]
            self.progress.update(task_id, completed=True)
    
    def __enter__(self):
        self.progress.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()

class APIKeyConfigurator:
    """Configurador interactivo de claves API"""
    
    def __init__(self, available_apis: Dict[str, Dict[str, str]]):
        self.available_apis = available_apis
        self.colors = get_theme()
    
    def configure_api(self, api_name: str) -> Optional[str]:
        """Configura una API específica"""
        if api_name not in self.available_apis:
            console.print(f"[{self.colors['error']}]❌ API '{api_name}' no encontrada[/]")
            return None
        
        api_info = self.available_apis[api_name]
        
        # Mostrar información de la API
        info_panel = f"""
[{self.colors['primary']}]🤖 Configurando {api_info['name']}[/]

[{self.colors['dim']}]Para obtener tu clave API:[/]
[{self.colors['info']}]• Visita el sitio web del proveedor[/]
[{self.colors['info']}]• Crea una cuenta o inicia sesión[/]
[{self.colors['info']}]• Genera una nueva clave API[/]
[{self.colors['info']}]• Copia la clave y pégala aquí[/]

[{self.colors['warning']}]⚠️ Mantén tu clave API segura y no la compartas[/]
"""
        
        console.print(create_panel(
            info_panel,
            title=f"Configuración de {api_info['name']}",
            style="chispart.brand"
        ))
        
        # Solicitar clave API
        api_key = InteractivePrompt.ask(
            f"Introduce tu clave API para {api_info['name']}",
            password=True
        )
        
        if not api_key or api_key.strip() == "":
            console.print(f"[{self.colors['warning']}]⚠️ Configuración cancelada[/]")
            return None
        
        return api_key.strip()
    
    def configure_multiple(self) -> Dict[str, str]:
        """Configura múltiples APIs interactivamente"""
        configured_keys = {}
        
        console.print(create_panel(
            f"[{self.colors['primary']}]🔧 Configuración de APIs[/]\n\n"
            f"[{self.colors['dim']}]Configura las claves API que desees usar.[/]\n"
            f"[{self.colors['dim']}]Puedes omitir las que no necesites por ahora.[/]",
            title="Configuración Inicial",
            style="chispart.brand"
        ))
        
        for api_key, api_info in self.available_apis.items():
            if InteractivePrompt.confirm(f"¿Configurar {api_info['name']}?", default=False):
                api_key_value = self.configure_api(api_key)
                if api_key_value:
                    configured_keys[api_info['default_key_env']] = api_key_value
                    console.print(f"[{self.colors['success']}]✅ {api_info['name']} configurada[/]")
        
        return configured_keys

class ThemeSelector:
    """Selector interactivo de temas"""
    
    def __init__(self, theme_manager):
        self.theme_manager = theme_manager
        self.colors = get_theme()
    
    def show_preview(self, theme_name: str):
        """Muestra una vista previa del tema"""
        if theme_name not in self.theme_manager.themes:
            return
        
        # Cambiar temporalmente al tema para la vista previa
        original_theme = self.theme_manager.current_theme
        self.theme_manager.current_theme = theme_name
        
        # Mostrar vista previa
        preview_colors = self.theme_manager.get_theme()
        
        preview_content = f"""
[{preview_colors['primary']}]● Primario[/] [{preview_colors['secondary']}]● Secundario[/] [{preview_colors['accent']}]● Acento[/]
[{preview_colors['success']}]✅ Éxito[/] [{preview_colors['warning']}]⚠️ Advertencia[/] [{preview_colors['error']}]❌ Error[/]
[{preview_colors['info']}]ℹ️ Información[/] [{preview_colors['dim']}]🔹 Texto secundario[/]

Ejemplo de comando:
[{preview_colors['primary']}]chispart[/] [{preview_colors['accent']}]chat[/] [{preview_colors['secondary']}]"¡Hola mundo!"[/]
"""
        
        console.print(create_panel(
            preview_content,
            title=f"Vista Previa: {theme_name}",
            style=preview_colors['primary']
        ))
        
        # Restaurar tema original
        self.theme_manager.current_theme = original_theme
    
    def select_theme(self) -> Optional[str]:
        """Permite seleccionar un tema interactivamente"""
        available_themes = self.theme_manager.get_available_themes()
        
        console.print(create_panel(
            f"[{self.colors['primary']}]🎨 Selector de Temas[/]\n\n"
            f"[{self.colors['dim']}]Elige el tema que más te guste para personalizar tu experiencia.[/]",
            title="Personalización",
            style="chispart.brand"
        ))
        
        # Mostrar temas disponibles
        for theme_name, description in available_themes.items():
            console.print(f"[{self.colors['info']}]{theme_name}[/]: {description}")
            
            if InteractivePrompt.confirm(f"¿Ver vista previa de '{theme_name}'?", default=False):
                self.show_preview(theme_name)
        
        # Selector de tema
        menu = MenuSelector(
            "🎨 Selecciona tu tema preferido",
            available_themes,
            "El tema se aplicará inmediatamente y se guardará como preferencia."
        )
        
        selected_theme = menu.show()
        
        if self.theme_manager.set_theme(selected_theme):
            console.print(f"[{self.colors['success']}]✅ Tema '{selected_theme}' aplicado correctamente[/]")
            return selected_theme
        else:
            console.print(f"[{self.colors['error']}]❌ Error al aplicar el tema[/]")
            return None

class SetupWizard:
    """Asistente de configuración inicial"""
    
    def __init__(self, available_apis: Dict[str, Dict[str, str]], theme_manager):
        self.available_apis = available_apis
        self.theme_manager = theme_manager
        self.colors = get_theme()
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el asistente de configuración completo"""
        console.print(create_panel(
            f"""
[{self.colors['primary']}]🚀 ¡Bienvenido a Chispart CLI![/]

[{self.colors['dim']}]Este asistente te ayudará a configurar tu CLI para que puedas empezar a usar múltiples APIs de IA de inmediato.[/]

[{self.colors['info']}]Configuraremos:[/]
[{self.colors['secondary']}]• 🎨 Tu tema preferido[/]
[{self.colors['secondary']}]• 🔑 Claves de API[/]
[{self.colors['secondary']}]• ⚙️ Preferencias básicas[/]
""",
            title="Configuración Inicial de Chispart",
            style="chispart.brand"
        ))
        
        if not InteractivePrompt.confirm("¿Continuar con la configuración?", default=True):
            return {}
        
        config_result = {}
        
        # 1. Selección de tema
        console.print(f"\n[{self.colors['primary']}]🎨 Paso 1: Personalización de Tema[/]")
        theme_selector = ThemeSelector(self.theme_manager)
        selected_theme = theme_selector.select_theme()
        if selected_theme:
            config_result['theme'] = selected_theme
        
        # 2. Configuración de APIs
        console.print(f"\n[{self.colors['primary']}]🔑 Paso 2: Configuración de APIs[/]")
        api_configurator = APIKeyConfigurator(self.available_apis)
        api_keys = api_configurator.configure_multiple()
        if api_keys:
            config_result['api_keys'] = api_keys
        
        # 3. Configuración completada
        console.print(create_panel(
            f"""
[{self.colors['success']}]🎉 ¡Configuración Completada![/]

[{self.colors['dim']}]Tu Chispart CLI está listo para usar. Puedes:[/]

[{self.colors['info']}]• Enviar mensajes: [/][{self.colors['primary']}]chispart chat "¡Hola!"[/]
[{self.colors['info']}]• Modo interactivo: [/][{self.colors['primary']}]chispart interactivo[/]
[{self.colors['info']}]• Ver ayuda: [/][{self.colors['primary']}]chispart --help[/]
[{self.colors['info']}]• Cambiar tema: [/][{self.colors['primary']}]chispart tema[/]

[{self.colors['accent']}]¡Disfruta usando Chispart CLI![/]
""",
            title="¡Listo para Usar!",
            style="chispart.success"
        ))
        
        return config_result
