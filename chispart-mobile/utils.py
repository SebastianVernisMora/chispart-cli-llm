"""
Utilidades para Chispart Mobile
Funciones de soporte para procesamiento de archivos, validación y almacenamiento
"""
import os
import json
import base64
import mimetypes
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Importaciones condicionales para diferentes entornos
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import PyMuPDF as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import pypdf
        PYPDF_AVAILABLE = True
        PYMUPDF_AVAILABLE = False
    except ImportError:
        PYMUPDF_AVAILABLE = False
        PYPDF_AVAILABLE = False

# Configuración de archivos soportados
SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
SUPPORTED_PDF_EXTENSIONS = ['.pdf']
MAX_FILE_SIZE_MB = 50  # Tamaño máximo por defecto

def is_supported_image(filename: str) -> bool:
    """
    Verifica si un archivo es una imagen soportada
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        True si es una imagen soportada
    """
    if not filename:
        return False
    
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_IMAGE_EXTENSIONS

def is_supported_pdf(filename: str) -> bool:
    """
    Verifica si un archivo es un PDF soportado
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        True si es un PDF soportado
    """
    if not filename:
        return False
    
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_PDF_EXTENSIONS

def validate_file_size(filepath: str, max_mb: int = MAX_FILE_SIZE_MB) -> bool:
    """
    Valida el tamaño de un archivo
    
    Args:
        filepath: Ruta al archivo
        max_mb: Tamaño máximo en MB
        
    Returns:
        True si el archivo está dentro del límite
    """
    try:
        if not os.path.exists(filepath):
            return False
        
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        
        return size_mb <= max_mb
    except Exception:
        return False

def format_file_size(size_bytes: int) -> str:
    """
    Formatea el tamaño de archivo en formato legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        Tamaño formateado (ej: "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def create_image_data_url(filepath: str) -> str:
    """
    Crea una data URL para una imagen
    
    Args:
        filepath: Ruta a la imagen
        
    Returns:
        Data URL de la imagen
        
    Raises:
        Exception: Si hay error procesando la imagen
    """
    try:
        if not os.path.exists(filepath):
            raise Exception(f"Archivo no encontrado: {filepath}")
        
        if not is_supported_image(filepath):
            raise Exception(f"Formato de imagen no soportado: {filepath}")
        
        # Obtener tipo MIME
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type or not mime_type.startswith('image/'):
            # Fallback basado en extensión
            ext = Path(filepath).suffix.lower()
            mime_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }
            mime_type = mime_map.get(ext, 'image/jpeg')
        
        # Leer y codificar imagen
        with open(filepath, 'rb') as f:
            image_data = f.read()
        
        # Optimizar imagen si PIL está disponible
        if PIL_AVAILABLE and len(image_data) > 5 * 1024 * 1024:  # > 5MB
            image_data = _optimize_image(filepath, max_size=(1920, 1080))
        
        # Crear data URL
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
        
    except Exception as e:
        raise Exception(f"Error creando data URL: {str(e)}")

def _optimize_image(filepath: str, max_size: tuple = (1920, 1080), quality: int = 85) -> bytes:
    """
    Optimiza una imagen reduciendo su tamaño
    
    Args:
        filepath: Ruta a la imagen
        max_size: Tamaño máximo (ancho, alto)
        quality: Calidad JPEG (1-100)
        
    Returns:
        Datos de imagen optimizada
    """
    if not PIL_AVAILABLE:
        # Si PIL no está disponible, devolver imagen original
        with open(filepath, 'rb') as f:
            return f.read()
    
    try:
        with Image.open(filepath) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar si es necesario
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Guardar optimizada en memoria
            from io import BytesIO
            output = BytesIO()
            
            # Determinar formato de salida
            format_map = {
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.png': 'PNG',
                '.webp': 'WEBP'
            }
            
            ext = Path(filepath).suffix.lower()
            output_format = format_map.get(ext, 'JPEG')
            
            if output_format == 'JPEG':
                img.save(output, format=output_format, quality=quality, optimize=True)
            else:
                img.save(output, format=output_format, optimize=True)
            
            return output.getvalue()
            
    except Exception:
        # En caso de error, devolver imagen original
        with open(filepath, 'rb') as f:
            return f.read()

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extrae texto de un archivo PDF
    
    Args:
        filepath: Ruta al archivo PDF
        
    Returns:
        Texto extraído del PDF
        
    Raises:
        Exception: Si hay error procesando el PDF
    """
    try:
        if not os.path.exists(filepath):
            raise Exception(f"Archivo no encontrado: {filepath}")
        
        if not is_supported_pdf(filepath):
            raise Exception(f"Archivo no es un PDF válido: {filepath}")
        
        text_content = ""
        
        # Intentar con PyMuPDF primero (más rápido y confiable)
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(filepath)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                    text_content += "\n\n"  # Separador entre páginas
                doc.close()
                return text_content.strip()
            except Exception as e:
                print(f"Error con PyMuPDF: {e}")
        
        # Fallback a pypdf
        if PYPDF_AVAILABLE:
            try:
                with open(filepath, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text_content += page.extract_text()
                        text_content += "\n\n"  # Separador entre páginas
                return text_content.strip()
            except Exception as e:
                print(f"Error con pypdf: {e}")
        
        # Si no hay librerías disponibles
        raise Exception("No hay librerías de PDF disponibles (PyMuPDF o pypdf)")
        
    except Exception as e:
        raise Exception(f"Error extrayendo texto del PDF: {str(e)}")

def save_conversation_history(conversation: Dict[str, Any]) -> bool:
    """
    Guarda una conversación en el historial
    
    Args:
        conversation: Diccionario con datos de la conversación
        
    Returns:
        True si se guardó exitosamente
    """
    try:
        # Obtener directorio de configuración
        config_dir = _get_config_directory()
        history_file = os.path.join(config_dir, 'chat_history.json')
        
        # Cargar historial existente
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Agregar nueva conversación
        conversation['id'] = len(history) + 1
        conversation['timestamp'] = conversation.get('timestamp', datetime.now().isoformat())
        history.append(conversation)
        
        # Limitar historial a últimas 1000 conversaciones
        if len(history) > 1000:
            history = history[-1000:]
        
        # Guardar historial actualizado
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"Error guardando historial: {e}")
        return False

def load_conversation_history(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Carga el historial de conversaciones
    
    Args:
        limit: Número máximo de conversaciones a cargar
        
    Returns:
        Lista de conversaciones
    """
    try:
        config_dir = _get_config_directory()
        history_file = os.path.join(config_dir, 'chat_history.json')
        
        if not os.path.exists(history_file):
            return []
        
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # Devolver las últimas conversaciones
        return history[-limit:] if len(history) > limit else history
        
    except Exception as e:
        print(f"Error cargando historial: {e}")
        return []

def clear_conversation_history() -> bool:
    """
    Limpia el historial de conversaciones
    
    Returns:
        True si se limpió exitosamente
    """
    try:
        config_dir = _get_config_directory()
        history_file = os.path.join(config_dir, 'chat_history.json')
        
        if os.path.exists(history_file):
            os.remove(history_file)
        
        return True
        
    except Exception as e:
        print(f"Error limpiando historial: {e}")
        return False

def _get_config_directory() -> str:
    """
    Obtiene el directorio de configuración
    
    Returns:
        Ruta al directorio de configuración
    """
    try:
        from termux_utils import get_termux_config_dir, is_termux
        if is_termux():
            return get_termux_config_dir()
    except ImportError:
        pass
    
    # Directorio por defecto
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, '.config', 'chispart-mobile')
    
    # Crear directorio si no existe
    os.makedirs(config_dir, exist_ok=True)
    
    return config_dir

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo removiendo caracteres peligrosos
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        Nombre de archivo sanitizado
    """
    import re
    
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remover espacios múltiples y puntos al inicio/final
    sanitized = re.sub(r'\s+', ' ', sanitized).strip('. ')
    
    # Limitar longitud
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized or 'unnamed_file'

def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Obtiene información detallada de un archivo
    
    Args:
        filepath: Ruta al archivo
        
    Returns:
        Diccionario con información del archivo
    """
    try:
        if not os.path.exists(filepath):
            return {'exists': False}
        
        stat = os.stat(filepath)
        
        return {
            'exists': True,
            'name': os.path.basename(filepath),
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'extension': Path(filepath).suffix.lower(),
            'is_image': is_supported_image(filepath),
            'is_pdf': is_supported_pdf(filepath),
            'mime_type': mimetypes.guess_type(filepath)[0]
        }
        
    except Exception as e:
        return {
            'exists': False,
            'error': str(e)
        }

def create_temp_file(content: bytes, extension: str = '.tmp') -> str:
    """
    Crea un archivo temporal
    
    Args:
        content: Contenido del archivo
        extension: Extensión del archivo
        
    Returns:
        Ruta al archivo temporal creado
    """
    import tempfile
    import uuid
    
    try:
        # Crear directorio temporal si no existe
        temp_dir = tempfile.gettempdir()
        
        # Generar nombre único
        filename = f"chispart_{uuid.uuid4().hex[:8]}{extension}"
        filepath = os.path.join(temp_dir, filename)
        
        # Escribir contenido
        with open(filepath, 'wb') as f:
            f.write(content)
        
        return filepath
        
    except Exception as e:
        raise Exception(f"Error creando archivo temporal: {str(e)}")

def cleanup_temp_files(pattern: str = "chispart_*") -> int:
    """
    Limpia archivos temporales
    
    Args:
        pattern: Patrón de archivos a limpiar
        
    Returns:
        Número de archivos eliminados
    """
    import tempfile
    import glob
    
    try:
        temp_dir = tempfile.gettempdir()
        pattern_path = os.path.join(temp_dir, pattern)
        
        files = glob.glob(pattern_path)
        count = 0
        
        for file in files:
            try:
                # Solo eliminar archivos más antiguos de 1 hora
                if os.path.exists(file):
                    age = time.time() - os.path.getmtime(file)
                    if age > 3600:  # 1 hora
                        os.remove(file)
                        count += 1
            except:
                continue
        
        return count
        
    except Exception:
        return 0

# Funciones de validación
def validate_api_key_format(api_key: str, api_name: str) -> bool:
    """
    Valida el formato de una API key
    
    Args:
        api_key: Clave API a validar
        api_name: Nombre del proveedor
        
    Returns:
        True si el formato es válido
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    api_key = api_key.strip()
    
    # Validaciones específicas por proveedor
    if api_name.lower() in ['blackbox', 'chispart']:
        # Blackbox API keys suelen empezar con 'sk-'
        return api_key.startswith('sk-') and len(api_key) > 10
    elif api_name.lower() == 'openai':
        # OpenAI API keys empiezan con 'sk-'
        return api_key.startswith('sk-') and len(api_key) > 40
    elif api_name.lower() == 'anthropic':
        # Anthropic API keys empiezan con 'sk-ant-'
        return api_key.startswith('sk-ant-') and len(api_key) > 20
    elif api_name.lower() == 'groq':
        # Groq API keys empiezan con 'gsk_'
        return api_key.startswith('gsk_') and len(api_key) > 20
    elif api_name.lower() == 'together':
        # Together AI keys son alfanuméricos largos
        return len(api_key) > 30 and api_key.replace('-', '').replace('_', '').isalnum()
    
    # Validación genérica
    return len(api_key) > 10

def validate_url(url: str) -> bool:
    """
    Valida si una URL tiene formato correcto
    
    Args:
        url: URL a validar
        
    Returns:
        True si la URL es válida
    """
    import re
    
    if not url or not isinstance(url, str):
        return False
    
    # Patrón básico para URLs
    pattern = re.compile(
        r'^https?://'  # http:// o https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # dominio
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # puerto opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return pattern.match(url) is not None

# Importar time para cleanup_temp_files
import time
