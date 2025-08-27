"""
Comandos para configuración y gestión del sistema
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from rich.prompt import Prompt, Confirm
from rich.table import Table

from ui.components import console, create_panel, create_table
from ui.theme_manager import ThemeManager, get_theme
from core.config_manager import ConfigManager
from core.validation import ValidationManager
from core.error_handler import ErrorHandler
from config import AVAILABLE_APIS, DEFAULT_API


class ConfigCommands:
    """Maneja comandos de configuración"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        self.validator = ValidationManager()
        self.error_handler = ErrorHandler()
        self.colors = get_theme()
    
    def handle_configure_api(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Configura una API específica o permite seleccionar
        
        Args:
            api_name: Nombre de la API (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Si no se especifica API, mostrar selector
            if not api_name:
                api_name = self._select_api_interactive()
                if not api_name:
                    return {"success": False, "error": "Configuración cancelada"}
            
            # Validar API
            if api_name not in AVAILABLE_APIS:
                error_msg = f"API '{api_name}' no reconocida"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
            
            # Configurar API
            return self._configure_single_api(api_name)
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "configure_api")
    
    def handle_list_apis(self) -> Dict[str, Any]:
        """Lista todas las APIs disponibles con su estado"""
        try:
            apis_info = []
            
            for api_key, api_config in AVAILABLE_APIS.items():
                # Verificar si está configurada
                config = self.config_manager.get_api_config(api_key)
                is_configured = bool(config.get("api_key"))
                
                apis_info.append({
                    "key": api_key,
                    "name": api_config["name"],
                    "configured": is_configured,
                    "default": api_key == DEFAULT_API
                })
            
            self._display_apis_table(apis_info)
            return {"success": True, "apis": apis_info}
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "list_apis")
    
    def handle_theme_change(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Cambia el tema de la interfaz
        
        Args:
            theme_name: Nombre del tema (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Si no se especifica tema, mostrar selector
            if not theme_name:
                theme_name = self._select_theme_interactive()
                if not theme_name:
                    return {"success": False, "error": "Cambio de tema cancelado"}
            
            # Aplicar tema
            if self.theme_manager.set_theme(theme_name):
                console.print(f"[{self.colors['success']}]✅ Tema cambiado a '{theme_name}'[/]")
                return {"success": True, "theme": theme_name}
            else:
                error_msg = f"Tema '{theme_name}' no encontrado"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return self.error_handler.handle_command_error(e, "theme_change")
    
    def handle_list_themes(self) -> Dict[str, Any]:
        """Lista todos los temas disponibles"""
        try:
            themes = self.theme_manager.get_available_themes()
            current_theme = self.theme_manager.get_current_theme()
            
            self._display_themes_table(themes, current_theme)
            return {"success": True, "themes": themes, "current": current_theme}
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "list_themes")
    
    def handle_show_config(self) -> Dict[str, Any]:
        """Muestra la configuración actual del sistema"""
        try:
            config_info = self.config_manager.get_system_info()
            self._display_config_info(config_info)
            return {"success": True, "config": config_info}
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "show_config")
    
    def handle_reset_config(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Resetea la configuración a valores por defecto
        
        Args:
            confirm: Si ya se confirmó la acción
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Pedir confirmación si no se proporcionó
            if not confirm:
                confirm = Confirm.ask(
                    f"[{self.colors['warning']}]⚠️ ¿Estás seguro de resetear toda la configuración?[/]",
                    default=False
                )
            
            if not confirm:
                console.print(f"[{self.colors['info']}]Operación cancelada[/]")
                return {"success": False, "error": "Operación cancelada"}
            
            # Resetear configuración
            self.config_manager.reset_to_defaults()
            console.print(f"[{self.colors['success']}]✅ Configuración reseteada exitosamente[/]")
            return {"success": True}
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "reset_config")
    
    def _select_api_interactive(self) -> Optional[str]:
        """Selector interactivo de API"""
        try:
            console.print(create_panel(
                "Selecciona la API que deseas configurar:",
                title="Configuración de API",
                style="chispart.brand"
            ))
            
            # Crear lista de opciones
            api_choices = []
            for api_key, api_config in AVAILABLE_APIS.items():
                config = self.config_manager.get_api_config(api_key)
                status = "✅ Configurada" if config.get("api_key") else "❌ No configurada"
                api_choices.append(f"{api_key} - {api_config['name']} ({status})")
            
            # Mostrar opciones
            for i, choice in enumerate(api_choices, 1):
                console.print(f"[{self.colors['dim']}]{i}.[/] {choice}")
            
            # Pedir selección
            selection = Prompt.ask(
                f"[{self.colors['primary']}]Selecciona una opción (1-{len(api_choices)}) o 'cancelar'[/]",
                default="cancelar"
            )
            
            if selection.lower() == "cancelar":
                return None
            
            try:
                index = int(selection) - 1
                if 0 <= index < len(api_choices):
                    return list(AVAILABLE_APIS.keys())[index]
            except ValueError:
                pass
            
            console.print(f"[{self.colors['error']}]Selección inválida[/]")
            return None
            
        except Exception:
            return None
    
    def _configure_single_api(self, api_name: str) -> Dict[str, Any]:
        """Configura una API específica"""
        try:
            api_config = AVAILABLE_APIS[api_name]
            
            console.print(create_panel(
                f"Configurando {api_config['name']}",
                title="Configuración de API",
                style="chispart.brand"
            ))
            
            # Mostrar información de la API
            console.print(f"[{self.colors['info']}]Variable de entorno:[/] {api_config['default_key_env']}")
            console.print(f"[{self.colors['info']}]URL base:[/] {api_config['base_url']}")
            
            # Pedir clave API
            api_key = Prompt.ask(
                f"[{self.colors['primary']}]Introduce tu clave API para {api_config['name']}[/]",
                password=True
            )
            
            if not api_key or api_key.strip() == "":
                console.print(f"[{self.colors['error']}]La clave API no puede estar vacía[/]")
                return {"success": False, "error": "Clave API vacía"}
            
            # Guardar configuración
            success = self.config_manager.set_api_key(api_name, api_key.strip())
            
            if success:
                console.print(f"[{self.colors['success']}]✅ API {api_config['name']} configurada exitosamente[/]")
                return {"success": True, "api": api_name}
            else:
                error_msg = "Error guardando la configuración"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _select_theme_interactive(self) -> Optional[str]:
        """Selector interactivo de tema"""
        try:
            themes = self.theme_manager.get_available_themes()
            current_theme = self.theme_manager.get_current_theme()
            
            console.print(create_panel(
                "Selecciona un tema para la interfaz:",
                title="Cambio de Tema",
                style="chispart.brand"
            ))
            
            # Mostrar temas disponibles
            for i, (theme_name, theme_info) in enumerate(themes.items(), 1):
                current_marker = " (actual)" if theme_name == current_theme else ""
                console.print(f"[{self.colors['dim']}]{i}.[/] {theme_name}{current_marker} - {theme_info.get('description', 'Sin descripción')}")
            
            # Pedir selección
            selection = Prompt.ask(
                f"[{self.colors['primary']}]Selecciona un tema (1-{len(themes)}) o 'cancelar'[/]",
                default="cancelar"
            )
            
            if selection.lower() == "cancelar":
                return None
            
            try:
                index = int(selection) - 1
                theme_names = list(themes.keys())
                if 0 <= index < len(theme_names):
                    return theme_names[index]
            except ValueError:
                pass
            
            console.print(f"[{self.colors['error']}]Selección inválida[/]")
            return None
            
        except Exception:
            return None
    
    def _display_apis_table(self, apis_info: List[Dict[str, Any]]):
        """Muestra tabla de APIs disponibles"""
        table = create_table("APIs Disponibles")
        table.add_column("API", style=self.colors['primary'])
        table.add_column("Nombre", style=self.colors['info'])
        table.add_column("Estado", style=self.colors['success'])
        table.add_column("Por Defecto", style=self.colors['warning'])
        
        for api in apis_info:
            status = "✅ Configurada" if api['configured'] else "❌ No configurada"
            default = "⭐ Sí" if api['default'] else ""
            
            table.add_row(
                api['key'],
                api['name'],
                status,
                default
            )
        
        console.print(table)
    
    def _display_themes_table(self, themes: Dict[str, Any], current_theme: str):
        """Muestra tabla de temas disponibles"""
        table = create_table("Temas Disponibles")
        table.add_column("Tema", style=self.colors['primary'])
        table.add_column("Descripción", style=self.colors['info'])
        table.add_column("Estado", style=self.colors['success'])
        
        for theme_name, theme_info in themes.items():
            status = "🎨 Actual" if theme_name == current_theme else ""
            description = theme_info.get('description', 'Sin descripción')
            
            table.add_row(theme_name, description, status)
        
        console.print(table)
    
    def _display_config_info(self, config_info: Dict[str, Any]):
        """Muestra información de configuración del sistema"""
        info_text = f"""
[{self.colors['primary']}]🔧 Configuración del Sistema[/]

[{self.colors['info']}]API por defecto:[/] {config_info.get('default_api', 'No configurada')}
[{self.colors['info']}]Tema actual:[/] {config_info.get('current_theme', 'No configurado')}
[{self.colors['info']}]Directorio de configuración:[/] {config_info.get('config_dir', 'No encontrado')}
[{self.colors['info']}]Archivo de historial:[/] {config_info.get('history_file', 'No encontrado')}

[{self.colors['primary']}]📊 APIs Configuradas:[/]
"""
        
        # Añadir información de APIs
        for api_name, is_configured in config_info.get('apis_status', {}).items():
            status = "✅" if is_configured else "❌"
            info_text += f"[{self.colors['dim']}]  {status} {api_name}[/]\n"
        
        console.print(create_panel(
            info_text.strip(),
            title="Información del Sistema",
            style=colors["info"]
        ))
