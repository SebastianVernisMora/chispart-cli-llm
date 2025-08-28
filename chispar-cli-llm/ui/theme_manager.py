"""
Sistema de gestión de temas para Chispart CLI
Proporciona temas personalizables y experiencia visual moderna
"""

import os
from typing import Dict, Any, Optional
from rich.theme import Theme
from rich.style import Style

class ChispartThemes:
    """Definición de temas para Chispart CLI"""
    
    # Tema Neón (por defecto) - Inspirado en el branding actual
    NEON = {
        "primary": "#00FF88",      # Verde neón principal
        "secondary": "#BB88FF",    # Púrpura neón
        "accent": "#FF88BB",       # Rosa neón
        "info": "#88FFFF",         # Cyan neón
        "success": "#00FF88",      # Verde éxito
        "warning": "#FFFF88",      # Amarillo neón
        "error": "#FF8888",        # Rojo neón
        "text": "#FFFFFF",         # Texto principal
        "dim": "#888888",          # Texto secundario
        "background": "#0A0A0A",   # Fondo oscuro
        "panel": "#1A1A1A",       # Paneles
        "border": "#333333"        # Bordes
    }
    
    # Tema Oscuro Profesional
    DARK_PRO = {
        "primary": "#007ACC",      # Azul VS Code
        "secondary": "#6C757D",    # Gris Bootstrap
        "accent": "#28A745",       # Verde Bootstrap
        "info": "#17A2B8",         # Info Bootstrap
        "success": "#28A745",      # Verde éxito
        "warning": "#FFC107",      # Amarillo Bootstrap
        "error": "#DC3545",        # Rojo Bootstrap
        "text": "#F8F9FA",         # Texto claro
        "dim": "#6C757D",          # Texto secundario
        "background": "#212529",   # Fondo oscuro
        "panel": "#343A40",        # Paneles
        "border": "#495057"        # Bordes
    }
    
    # Tema Claro Minimalista
    LIGHT = {
        "primary": "#0066CC",      # Azul principal
        "secondary": "#6C757D",    # Gris
        "accent": "#28A745",       # Verde
        "info": "#17A2B8",         # Info
        "success": "#28A745",      # Verde éxito
        "warning": "#FFC107",      # Amarillo
        "error": "#DC3545",        # Rojo
        "text": "#212529",         # Texto oscuro
        "dim": "#6C757D",          # Texto secundario
        "background": "#FFFFFF",   # Fondo claro
        "panel": "#F8F9FA",        # Paneles
        "border": "#DEE2E6"        # Bordes
    }
    
    # Tema Terminal Retro
    RETRO = {
        "primary": "#00FF00",      # Verde terminal clásico
        "secondary": "#FFFF00",    # Amarillo terminal
        "accent": "#FF00FF",       # Magenta
        "info": "#00FFFF",         # Cyan
        "success": "#00FF00",      # Verde éxito
        "warning": "#FFFF00",      # Amarillo
        "error": "#FF0000",        # Rojo
        "text": "#00FF00",         # Verde terminal
        "dim": "#008000",          # Verde oscuro
        "background": "#000000",   # Negro terminal
        "panel": "#001100",        # Verde muy oscuro
        "border": "#004400"        # Verde oscuro
    }

class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    def __init__(self):
        self.themes = {
            "neon": ChispartThemes.NEON,
            "dark": ChispartThemes.DARK_PRO,
            "light": ChispartThemes.LIGHT,
            "retro": ChispartThemes.RETRO
        }
        self.current_theme = "neon"  # Tema por defecto
        self._load_user_preference()
    
    def _load_user_preference(self):
        """Carga la preferencia de tema del usuario"""
        try:
            theme_file = os.path.expanduser("~/.chispart/theme")
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    saved_theme = f.read().strip()
                    if saved_theme in self.themes:
                        self.current_theme = saved_theme
        except Exception:
            pass  # Usar tema por defecto si hay error
    
    def save_user_preference(self, theme_name: str):
        """Guarda la preferencia de tema del usuario"""
        try:
            os.makedirs(os.path.expanduser("~/.chispart"), exist_ok=True)
            theme_file = os.path.expanduser("~/.chispart/theme")
            with open(theme_file, 'w') as f:
                f.write(theme_name)
        except Exception:
            pass  # Ignorar errores de guardado
    
    def set_theme(self, theme_name: str) -> bool:
        """Establece el tema actual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.save_user_preference(theme_name)
            return True
        return False
    
    def get_theme(self) -> Dict[str, str]:
        """Obtiene el tema actual"""
        return self.themes[self.current_theme]
    
    def get_rich_theme(self) -> Theme:
        """Obtiene el tema en formato Rich"""
        theme_colors = self.get_theme()
        
        return Theme({
            # Estilos básicos
            "primary": theme_colors["primary"],
            "secondary": theme_colors["secondary"],
            "accent": theme_colors["accent"],
            "info": theme_colors["info"],
            "success": theme_colors["success"],
            "warning": theme_colors["warning"],
            "error": theme_colors["error"],
            "text": theme_colors["text"],
            "dim": theme_colors["dim"],
            
            # Estilos específicos de Chispart
            "chispart.brand": f"bold {theme_colors['primary']}",
            "chispart.title": f"bold {theme_colors['primary']}",
            "chispart.subtitle": theme_colors["secondary"],
            "chispart.highlight": f"bold {theme_colors['accent']}",
            "chispart.status": theme_colors["info"],
            "chispart.success": f"bold {theme_colors['success']}",
            "chispart.warning": f"bold {theme_colors['warning']}",
            "chispart.error": f"bold {theme_colors['error']}",
            "chispart.dim": theme_colors["dim"],
            
            # Estilos para paneles
            "panel.border": theme_colors["border"],
            "panel.title": f"bold {theme_colors['primary']}",
            
            # Estilos para tablas
            "table.header": f"bold {theme_colors['primary']}",
            "table.row": theme_colors["text"],
            "table.row_alt": theme_colors["dim"],
            
            # Estilos para progress bars
            "progress.bar": theme_colors["primary"],
            "progress.complete": theme_colors["success"],
            "progress.remaining": theme_colors["dim"],
            
            # Estilos para comandos
            "command": f"bold {theme_colors['accent']}",
            "option": theme_colors["secondary"],
            "argument": theme_colors["info"],
            
            # Estilos para APIs
            "api.openai": "#00A67E",
            "api.anthropic": "#D97706",
            "api.groq": "#F59E0B",
            "api.together": "#8B5CF6",
            "api.blackbox": theme_colors["primary"],
            "api.chispart": theme_colors["primary"],
        })
    
    def get_available_themes(self) -> Dict[str, str]:
        """Obtiene la lista de temas disponibles con descripciones"""
        return {
            "neon": "🌈 Tema Neón - Colores vibrantes y modernos (por defecto)",
            "dark": "🌙 Tema Oscuro Profesional - Elegante y fácil para los ojos",
            "light": "☀️ Tema Claro Minimalista - Limpio y profesional",
            "retro": "💻 Tema Terminal Retro - Nostálgico estilo terminal clásico"
        }
    
    def preview_theme(self, theme_name: str) -> str:
        """Genera una vista previa del tema"""
        if theme_name not in self.themes:
            return "❌ Tema no encontrado"
        
        colors = self.themes[theme_name]
        preview = f"""
🎨 Vista previa del tema '{theme_name}':

[{colors['primary']}]● Primario[/] [{colors['secondary']}]● Secundario[/] [{colors['accent']}]● Acento[/]
[{colors['success']}]✅ Éxito[/] [{colors['warning']}]⚠️ Advertencia[/] [{colors['error']}]❌ Error[/]
[{colors['info']}]ℹ️ Información[/] [{colors['dim']}]🔹 Texto secundario[/]

Ejemplo de uso:
[{colors['primary']}]chispart[/] [{colors['accent']}]chat[/] [{colors['secondary']}]"¡Hola mundo!"[/]
"""
        return preview

# Instancia global del gestor de temas
_theme_manager = ThemeManager()

def get_theme_manager() -> ThemeManager:
    """Obtiene la instancia global del gestor de temas"""
    return _theme_manager

def get_theme() -> Dict[str, str]:
    """Función de conveniencia para obtener el tema actual"""
    return _theme_manager.get_theme()

def get_rich_theme() -> Theme:
    """Función de conveniencia para obtener el tema Rich actual"""
    return _theme_manager.get_rich_theme()

def set_theme(theme_name: str) -> bool:
    """Función de conveniencia para establecer el tema"""
    return _theme_manager.set_theme(theme_name)
