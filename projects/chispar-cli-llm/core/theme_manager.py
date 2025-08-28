"""
Sistema de Gestión de Temas para Chispart CLI
"""

from typing import Dict, Optional
from rich.console import Console
from rich.theme import Theme

class ThemeManager:
    """Gestor de temas para la interfaz CLI"""
    
    def __init__(self):
        self.current_theme = "neon"
        self.themes = {
            "neon": Theme({
                "info": "cyan",
                "warning": "yellow",
                "error": "red",
                "success": "green",
                "primary": "bright_cyan",
                "secondary": "magenta"
            }),
            "dark": Theme({
                "info": "blue",
                "warning": "yellow",
                "error": "red",
                "success": "green",
                "primary": "white",
                "secondary": "bright_black"
            }),
            "light": Theme({
                "info": "blue",
                "warning": "dark_orange",
                "error": "red",
                "success": "dark_green",
                "primary": "black",
                "secondary": "grey50"
            }),
            "retro": Theme({
                "info": "bright_blue",
                "warning": "bright_yellow",
                "error": "bright_red",
                "success": "bright_green",
                "primary": "bright_white",
                "secondary": "bright_magenta"
            })
        }
    
    def set_theme(self, theme_name: str) -> bool:
        """Establece el tema actual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_theme(self, theme_name: Optional[str] = None) -> Theme:
        """Obtiene un tema específico"""
        name = theme_name or self.current_theme
        return self.themes.get(name, self.themes["neon"])
    
    def get_current_theme_name(self) -> str:
        """Obtiene el nombre del tema actual"""
        return self.current_theme
    
    def list_themes(self) -> Dict[str, str]:
        """Lista todos los temas disponibles"""
        return {
            "neon": "Colores neón vibrantes",
            "dark": "Tema oscuro elegante", 
            "light": "Tema claro minimalista",
            "retro": "Estilo retro nostálgico"
        }

# Instancia global
theme_manager = ThemeManager()
