"""
Utilidades para el manejo de archivos y funciones auxiliares
Optimizado para Termux y dispositivos móviles
"""
import base64
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from config import SUPPORTED_IMAGE_TYPES, SUPPORTED_PDF_TYPES

# Importar PyMuPDF (rápido, con dependencias C)
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Importar pypdf (alternativa pura de Python, ideal para Termux)
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

if not PYMUPDF_AVAILABLE and not PYPDF_AVAILABLE:
    print("⚠️  No se encontró ninguna biblioteca para procesar PDF (PyMuPDF, pypdf).")
    print("   El análisis de PDF no estará disponible.")
    print("   Instala una de las dos: pip install PyMuPDF | pip install pypdf")

# Importar utilidades de Termux
try:
    from termux_utils import (
        get_safe_temp_path, ensure_directory_exists, 
        optimize_file_size_limits, is_termux
    )
    TERMUX_UTILS_AVAILABLE = True
except ImportError:
    TERMUX_UTILS_AVAILABLE = False
    
    # Fallbacks si termux_utils no está disponible
    def get_safe_temp_path(filename: str) -> str:
        return f"/tmp/{filename}"
    
    def ensure_directory_exists(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except:
            return False
    
    def optimize_file_size_limits() -> Dict[str, int]:
        return {
            'max_image_size_mb': 20,
            'max_pdf_size_mb': 20,
            'max_text_chars': 100000
        }
    
    def is_termux() -> bool:
        return False


def encode_file_to_base64(file_path: str) -> str:
    """
    Codifica un archivo a base64
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Contenido del archivo codificado en base64
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        IOError: Si hay problemas leyendo el archivo
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")
    
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except IOError as e:
        raise IOError(f"Error leyendo el archivo {file_path}: {str(e)}")


def create_image_data_url(file_path: str) -> str:
    """
    Crea una URL de datos para una imagen
    
    Args:
        file_path: Ruta de la imagen
        
    Returns:
        URL de datos en formato data:image/tipo;base64,contenido
    """
    file_ext = Path(file_path).suffix.lower()
    
    # Determinar el tipo MIME
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp'
    }
    
    mime_type = mime_types.get(file_ext, 'image/jpeg')
    base64_content = encode_file_to_base64(file_path)
    
    return f"data:{mime_type};base64,{base64_content}"


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrae el texto de un archivo PDF.
    Usa PyMuPDF si está disponible (más rápido), o pypdf como alternativa (más compatible).

    Args:
        file_path: Ruta del archivo PDF.

    Returns:
        El texto extraído del PDF.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        Exception: Si no hay bibliotecas de PDF disponibles o hay un error.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")

    text = ""
    try:
        if PYMUPDF_AVAILABLE:
            # Usar PyMuPDF (fitz) - es más rápido y robusto
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif PYPDF_AVAILABLE:
            # Usar pypdf - alternativa pura de Python
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            raise Exception(
                "No hay una biblioteca de procesamiento de PDF disponible.\n"
                "Instala una con: pip install PyMuPDF o pip install pypdf"
            )

        # Aplicar límites optimizados para móviles
        limits = optimize_file_size_limits()
        max_chars = limits['max_text_chars']

        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... CONTENIDO TRUNCADO PARA OPTIMIZAR RENDIMIENTO ...]"
            if is_termux():
                print(f"⚠️  Texto truncado a {max_chars} caracteres para optimizar rendimiento en móvil")

        return text
    except Exception as e:
        raise Exception(f"No se pudo procesar el archivo PDF {file_path}: {str(e)}")


def is_supported_image(file_path: str) -> bool:
    """
    Verifica si un archivo es una imagen soportada
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es una imagen soportada, False en caso contrario
    """
    file_ext = Path(file_path).suffix.lower()
    return file_ext in SUPPORTED_IMAGE_TYPES


def is_supported_pdf(file_path: str) -> bool:
    """
    Verifica si un archivo es un PDF soportado
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es un PDF soportado, False en caso contrario
    """
    file_ext = Path(file_path).suffix.lower()
    return file_ext in SUPPORTED_PDF_TYPES


def save_conversation_history(conversation: Dict[str, Any], history_file: str = "chat_history.json"):
    """
    Guarda una conversación en el historial
    
    Args:
        conversation: Datos de la conversación
        history_file: Archivo donde guardar el historial
    """
    # Agregar timestamp
    conversation["timestamp"] = datetime.now().isoformat()
    
    # Cargar historial existente o crear uno nuevo
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    
    # Agregar nueva conversación
    history.append(conversation)
    
    # Guardar historial actualizado
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Advertencia: No se pudo guardar el historial: {str(e)}")


def load_conversation_history(history_file: str = "chat_history.json") -> list:
    """
    Carga el historial de conversaciones
    
    Args:
        history_file: Archivo del historial
        
    Returns:
        Lista de conversaciones
    """
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def format_file_size(size_bytes: int) -> str:
    """
    Formatea el tamaño de archivo en una forma legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        Tamaño formateado (ej: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_file_size(file_path: str, max_size_mb: Optional[int] = None) -> bool:
    """
    Valida que un archivo no exceda el tamaño máximo
    Usa límites optimizados para Termux automáticamente
    
    Args:
        file_path: Ruta del archivo
        max_size_mb: Tamaño máximo en MB (None para usar límites optimizados)
        
    Returns:
        True si el archivo es válido, False en caso contrario
    """
    if not os.path.exists(file_path):
        return False
    
    # Usar límites optimizados si no se especifica
    if max_size_mb is None:
        limits = optimize_file_size_limits()
        # Determinar el tipo de archivo y usar el límite apropiado
        file_ext = Path(file_path).suffix.lower()
        if file_ext in SUPPORTED_IMAGE_TYPES:
            max_size_mb = limits['max_image_size_mb']
        elif file_ext in SUPPORTED_PDF_TYPES:
            max_size_mb = limits['max_pdf_size_mb']
        else:
            max_size_mb = 20  # Fallback
    
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    
    return file_size <= max_size_bytes
