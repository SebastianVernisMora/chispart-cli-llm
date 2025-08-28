"""
Comandos para manejo de archivos (imágenes y PDFs)
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from ui.components import console, create_panel, create_progress_bar
from ui.theme_manager import get_theme
from core.validation import APIValidator
from core.error_handler import ChispartErrorHandler
from utils import (
    is_supported_image, is_supported_pdf, 
    validate_file_size, format_file_size
)


class FileCommands:
    """Maneja comandos relacionados con archivos"""
    
    def __init__(self, command_handler):
        self.command_handler = command_handler
        self.validator = APIValidator()
        self.error_handler = ChispartErrorHandler()
        self.colors = get_theme()
    
    def handle_image_analysis(self, api_name: str, file_path: str, 
                            prompt: str, model: Optional[str] = None,
                            save_history: bool = True) -> Dict[str, Any]:
        """
        Maneja el análisis de imágenes
        
        Args:
            api_name: Nombre de la API a utilizar
            file_path: Ruta del archivo de imagen
            prompt: Pregunta sobre la imagen
            model: Modelo específico (opcional)
            save_history: Si guardar en historial
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar archivo
            validation_result = self._validate_image_file(file_path)
            if not validation_result["valid"]:
                console.print(f"[{self.colors['error']}]{validation_result['error']}[/]")
                return {"success": False, "error": validation_result["error"]}
            
            # Validar API soporta imágenes
            if not self.validator.validate_vision_support(api_name):
                error_msg = f"La API {api_name} no soporta análisis de imágenes"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
            
            # Mostrar información del archivo
            self._show_file_info(file_path, "imagen")
            
            # Procesar con la API
            return self.command_handler.handle_image_analysis(
                api_name=api_name,
                file_path=file_path,
                prompt=prompt,
                model=model,
                save_history=save_history
            )
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "image_analysis")
    
    def handle_pdf_analysis(self, api_name: str, file_path: str,
                          prompt: str, model: Optional[str] = None,
                          save_history: bool = True) -> Dict[str, Any]:
        """
        Maneja el análisis de PDFs
        
        Args:
            api_name: Nombre de la API a utilizar
            file_path: Ruta del archivo PDF
            prompt: Pregunta sobre el PDF
            model: Modelo específico (opcional)
            save_history: Si guardar en historial
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar archivo
            validation_result = self._validate_pdf_file(file_path)
            if not validation_result["valid"]:
                console.print(f"[{self.colors['error']}]{validation_result['error']}[/]")
                return {"success": False, "error": validation_result["error"]}
            
            # Validar API soporta PDFs
            if not self.validator.validate_pdf_support(api_name):
                error_msg = f"La API {api_name} no soporta análisis de PDFs"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
            
            # Mostrar información del archivo
            self._show_file_info(file_path, "PDF")
            
            # Procesar con la API
            return self.command_handler.handle_pdf_analysis(
                api_name=api_name,
                file_path=file_path,
                prompt=prompt,
                model=model,
                save_history=save_history
            )
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "pdf_analysis")
    
    def _validate_image_file(self, file_path: str) -> Dict[str, Any]:
        """Valida un archivo de imagen"""
        try:
            # Verificar existencia
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "error": f"El archivo {file_path} no existe"
                }
            
            # Verificar formato
            if not is_supported_image(file_path):
                return {
                    "valid": False,
                    "error": "Formato de imagen no soportado. Use: JPG, JPEG, PNG, WebP"
                }
            
            # Verificar tamaño
            if not validate_file_size(file_path, 20):  # 20MB máximo
                file_size = format_file_size(os.path.getsize(file_path))
                return {
                    "valid": False,
                    "error": f"Archivo demasiado grande ({file_size}). Máximo: 20MB"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validando imagen: {str(e)}"
            }
    
    def _validate_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Valida un archivo PDF"""
        try:
            # Verificar existencia
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "error": f"El archivo {file_path} no existe"
                }
            
            # Verificar formato
            if not is_supported_pdf(file_path):
                return {
                    "valid": False,
                    "error": "El archivo debe ser un PDF válido"
                }
            
            # Verificar tamaño
            if not validate_file_size(file_path, 20):  # 20MB máximo
                file_size = format_file_size(os.path.getsize(file_path))
                return {
                    "valid": False,
                    "error": f"Archivo demasiado grande ({file_size}). Máximo: 20MB"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validando PDF: {str(e)}"
            }
    
    def _show_file_info(self, file_path: str, file_type: str):
        """Muestra información del archivo a procesar"""
        try:
            file_path_obj = Path(file_path)
            file_size = format_file_size(file_path_obj.stat().st_size)
            
            info = f"""
[{self.colors['info']}]📁 Archivo:[/] {file_path_obj.name}
[{self.colors['info']}]📏 Tamaño:[/] {file_size}
[{self.colors['info']}]📂 Tipo:[/] {file_type}
[{self.colors['info']}]📍 Ruta:[/] {file_path_obj.absolute()}
"""
            
            console.print(create_panel(
                info.strip(),
                title=f"Información del {file_type}",
                style=colors["info"]
            ))
            
        except Exception:
            # Si hay error mostrando info, continuar silenciosamente
            pass
    
    def list_supported_formats(self):
        """Muestra los formatos de archivo soportados"""
        formats_info = f"""
[{self.colors['primary']}]🖼️ Formatos de Imagen Soportados:[/]
[{self.colors['success']}]• JPG / JPEG[/] - Formato estándar de fotografías
[{self.colors['success']}]• PNG[/] - Formato con transparencia
[{self.colors['success']}]• WebP[/] - Formato moderno optimizado

[{self.colors['primary']}]📄 Formatos de Documento Soportados:[/]
[{self.colors['success']}]• PDF[/] - Documentos portátiles

[{self.colors['warning']}]⚠️ Limitaciones:[/]
[{self.colors['dim']}]• Tamaño máximo: 20MB por archivo[/]
[{self.colors['dim']}]• Las imágenes requieren APIs con soporte de visión[/]
[{self.colors['dim']}]• Los PDFs se procesan extrayendo el texto[/]

[{self.colors['info']}]💡 Consejos:[/]
[{self.colors['dim']}]• Use imágenes claras y bien iluminadas[/]
[{self.colors['dim']}]• Los PDFs con texto seleccionable funcionan mejor[/]
[{self.colors['dim']}]• Comprima archivos grandes antes de procesarlos[/]
"""
        
        console.print(create_panel(
            formats_info.strip(),
            title="Formatos de Archivo Soportados",
            style="chispart.brand"
        ))
