"""
Manejador de errores centralizado para Chispart CLI
"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from api_client import APIError
from .validation import ValidationError
from ui.components import console
from ui.theme_manager import get_theme

class ChispartErrorHandler:
    """Manejador centralizado de errores con UI mejorada"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.colors = get_theme()
        self.error_count = 0
        self.last_error = None
    
    def handle_api_error(self, error: APIError, context: Optional[Dict[str, Any]] = None) -> None:
        """Maneja errores de API con mensajes informativos"""
        self.error_count += 1
        self.last_error = error
        
        # Mensaje principal
        console.print(f"[{self.colors['error']}]❌ Error de API ({error.api_name})[/]")
        console.print(f"[{self.colors['dim']}]{error.message}[/]")
        
        # Información adicional según el código de estado
        if error.status_code:
            status_info = self._get_status_info(error.status_code)
            if status_info:
                console.print(f"[{self.colors['info']}]💡 {status_info}[/]")
        
        # Sugerencias específicas por API
        suggestions = self._get_api_suggestions(error.api_name, error.status_code)
        if suggestions:
            console.print(f"[{self.colors['warning']}]💡 Sugerencias:[/]")
            for suggestion in suggestions:
                console.print(f"[{self.colors['dim']}]  • {suggestion}[/]")
        
        # Información de contexto si está disponible
        if context:
            self._print_context_info(context)
        
        # Información de debug si está habilitada
        if self.debug_mode:
            self._print_debug_info(error)
    
    def handle_validation_error(self, error: ValidationError, context: Optional[Dict[str, Any]] = None) -> None:
        """Maneja errores de validación"""
        self.error_count += 1
        self.last_error = error
        
        console.print(f"[{self.colors['error']}]❌ Error de Validación[/]")
        console.print(f"[{self.colors['dim']}]{error.message}[/]")
        
        if error.suggestion:
            console.print(f"[{self.colors['info']}]💡 {error.suggestion}[/]")
        
        if context:
            self._print_context_info(context)
    
    def handle_file_error(self, error: Exception, file_path: str, operation: str = "procesar") -> None:
        """Maneja errores relacionados con archivos"""
        self.error_count += 1
        self.last_error = error
        
        console.print(f"[{self.colors['error']}]❌ Error al {operation} archivo[/]")
        console.print(f"[{self.colors['dim']}]Archivo: {file_path}[/]")
        console.print(f"[{self.colors['dim']}]Error: {str(error)}[/]")
        
        # Sugerencias específicas para errores de archivo
        suggestions = self._get_file_error_suggestions(error, file_path)
        if suggestions:
            console.print(f"[{self.colors['warning']}]💡 Sugerencias:[/]")
            for suggestion in suggestions:
                console.print(f"[{self.colors['dim']}]  • {suggestion}[/]")
    
    def handle_network_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Maneja errores de red"""
        self.error_count += 1
        self.last_error = error
        
        console.print(f"[{self.colors['error']}]❌ Error de Conexión[/]")
        console.print(f"[{self.colors['dim']}]{str(error)}[/]")
        
        # Sugerencias para problemas de red
        suggestions = [
            "Verifica tu conexión a internet",
            "Intenta cambiar de WiFi a datos móviles o viceversa",
            "Si estás en Termux, verifica que tengas permisos de red",
            "Algunos proveedores pueden bloquear ciertas APIs"
        ]
        
        console.print(f"[{self.colors['warning']}]💡 Sugerencias:[/]")
        for suggestion in suggestions:
            console.print(f"[{self.colors['dim']}]  • {suggestion}[/]")
        
        if context:
            self._print_context_info(context)
    
    def handle_unexpected_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Maneja errores inesperados"""
        self.error_count += 1
        self.last_error = error
        
        console.print(f"[{self.colors['error']}]❌ Error Inesperado[/]")
        console.print(f"[{self.colors['dim']}]{str(error)}[/]")
        
        if self.debug_mode:
            console.print(f"[{self.colors['dim']}]Traceback:[/]")
            console.print(f"[{self.colors['dim']}]{traceback.format_exc()}[/]")
        else:
            console.print(f"[{self.colors['info']}]💡 Usa --debug para ver más detalles[/]")
        
        # Sugerencias generales
        suggestions = [
            "Intenta ejecutar el comando de nuevo",
            "Verifica que todos los parámetros sean correctos",
            "Si el problema persiste, reporta el error en GitHub"
        ]
        
        console.print(f"[{self.colors['warning']}]💡 Sugerencias:[/]")
        for suggestion in suggestions:
            console.print(f"[{self.colors['dim']}]  • {suggestion}[/]")
        
        if context:
            self._print_context_info(context)
    
    def handle_keyboard_interrupt(self) -> None:
        """Maneja interrupciones del usuario (Ctrl+C)"""
        console.print(f"\n[{self.colors['warning']}]⚠️ Operación cancelada por el usuario[/]")
        console.print(f"[{self.colors['dim']}]¡Hasta luego![/]")
    
    def _get_status_info(self, status_code: int) -> Optional[str]:
        """Obtiene información sobre códigos de estado HTTP"""
        status_messages = {
            400: "Solicitud inválida - Verifica los parámetros enviados",
            401: "No autorizado - Verifica tu clave API",
            403: "Prohibido - Tu clave API no tiene permisos suficientes",
            404: "No encontrado - El endpoint o recurso no existe",
            429: "Demasiadas solicitudes - Has excedido el límite de rate",
            500: "Error del servidor - Problema temporal del proveedor",
            502: "Bad Gateway - Problema de conectividad del proveedor",
            503: "Servicio no disponible - El proveedor está en mantenimiento"
        }
        return status_messages.get(status_code)
    
    def _get_api_suggestions(self, api_name: str, status_code: Optional[int] = None) -> list:
        """Obtiene sugerencias específicas por API"""
        suggestions = []
        
        if status_code == 401:
            suggestions.append(f"Verifica que tu clave API para {api_name} sea correcta")
            suggestions.append("Usa 'chispart configure' para reconfigurar tus claves")
        
        elif status_code == 429:
            suggestions.append("Espera unos minutos antes de intentar de nuevo")
            suggestions.append("Considera usar una API diferente temporalmente")
        
        elif status_code == 403:
            if api_name.lower() == "openai":
                suggestions.append("Verifica que tengas créditos disponibles en tu cuenta OpenAI")
            elif api_name.lower() == "anthropic":
                suggestions.append("Verifica que tengas acceso a la API de Anthropic")
        
        # Sugerencias generales por API
        if api_name.lower() == "chispart":
            suggestions.append("Verifica que tu clave BlackboxAI sea válida")
        elif api_name.lower() == "groq":
            suggestions.append("Groq tiene límites estrictos - intenta con mensajes más cortos")
        
        return suggestions
    
    def _get_file_error_suggestions(self, error: Exception, file_path: str) -> list:
        """Obtiene sugerencias para errores de archivo"""
        suggestions = []
        error_str = str(error).lower()
        
        if "permission" in error_str or "access" in error_str:
            suggestions.append("Verifica que tengas permisos de lectura para el archivo")
            suggestions.append("En Termux, usa 'termux-setup-storage' para acceder a archivos del teléfono")
        
        elif "not found" in error_str or "no such file" in error_str:
            suggestions.append("Verifica que la ruta del archivo sea correcta")
            suggestions.append("Usa rutas absolutas o relativas válidas")
            suggestions.append("En Termux, los archivos del teléfono están en ~/storage/shared/")
        
        elif "too large" in error_str or "size" in error_str:
            suggestions.append("El archivo es demasiado grande - intenta con uno más pequeño")
            suggestions.append("Para PDFs, considera dividir el documento")
        
        elif "format" in error_str or "invalid" in error_str:
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                suggestions.append("Verifica que la imagen no esté corrupta")
                suggestions.append("Intenta con otro formato de imagen (JPG, PNG, WebP)")
            elif file_path.lower().endswith('.pdf'):
                suggestions.append("Verifica que el PDF no esté corrupto o protegido")
                suggestions.append("Intenta con otro archivo PDF")
        
        return suggestions
    
    def _print_context_info(self, context: Dict[str, Any]) -> None:
        """Imprime información de contexto"""
        if not context:
            return
        
        console.print(f"[{self.colors['dim']}]Contexto:[/]")
        for key, value in context.items():
            if key not in ['api_key', 'password']:  # No mostrar información sensible
                console.print(f"[{self.colors['dim']}]  {key}: {value}[/]")
    
    def _print_debug_info(self, error: Exception) -> None:
        """Imprime información de debug"""
        console.print(f"[{self.colors['dim']}]Debug Info:[/]")
        console.print(f"[{self.colors['dim']}]  Tipo: {type(error).__name__}[/]")
        console.print(f"[{self.colors['dim']}]  Timestamp: {datetime.now().isoformat()}[/]")
        
        if hasattr(error, '__dict__'):
            for attr, value in error.__dict__.items():
                if attr not in ['api_key']:  # No mostrar información sensible
                    console.print(f"[{self.colors['dim']}]  {attr}: {value}[/]")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de errores"""
        return {
            "error_count": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None,
            "last_error_type": type(self.last_error).__name__ if self.last_error else None
        }
    
    def reset_error_count(self) -> None:
        """Resetea el contador de errores"""
        self.error_count = 0
        self.last_error = None

# Decorador para manejo automático de errores
def handle_errors(error_handler: ChispartErrorHandler, exit_on_error: bool = True):
    """
    Decorador para manejo automático de errores en comandos
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                error_handler.handle_keyboard_interrupt()
                if exit_on_error:
                    sys.exit(130)  # Código estándar para Ctrl+C
            except APIError as e:
                error_handler.handle_api_error(e, {"function": func.__name__})
                if exit_on_error:
                    sys.exit(1)
            except ValidationError as e:
                error_handler.handle_validation_error(e, {"function": func.__name__})
                if exit_on_error:
                    sys.exit(1)
            except FileNotFoundError as e:
                error_handler.handle_file_error(e, str(e), "encontrar")
                if exit_on_error:
                    sys.exit(1)
            except PermissionError as e:
                error_handler.handle_file_error(e, str(e), "acceder")
                if exit_on_error:
                    sys.exit(1)
            except (ConnectionError, TimeoutError) as e:
                error_handler.handle_network_error(e, {"function": func.__name__})
                if exit_on_error:
                    sys.exit(1)
            except Exception as e:
                error_handler.handle_unexpected_error(e, {"function": func.__name__})
                if exit_on_error:
                    sys.exit(1)
        
        return wrapper
    return decorator

# Instancia global del manejador de errores
global_error_handler = ChispartErrorHandler()

# Funciones de conveniencia
def handle_api_error(error: APIError, context: Optional[Dict[str, Any]] = None) -> None:
    """Función de conveniencia para manejar errores de API"""
    global_error_handler.handle_api_error(error, context)

def handle_validation_error(error: ValidationError, context: Optional[Dict[str, Any]] = None) -> None:
    """Función de conveniencia para manejar errores de validación"""
    global_error_handler.handle_validation_error(error, context)

def handle_file_error(error: Exception, file_path: str, operation: str = "procesar") -> None:
    """Función de conveniencia para manejar errores de archivo"""
    global_error_handler.handle_file_error(error, file_path, operation)

def handle_unexpected_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Función de conveniencia para manejar errores inesperados"""
    global_error_handler.handle_unexpected_error(error, context)

def set_debug_mode(debug: bool) -> None:
    """Configura el modo debug globalmente"""
    global_error_handler.debug_mode = debug
