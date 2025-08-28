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

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from config_extended import SUPPORTED_IMAGE_TYPES, SUPPORTED_PDF_TYPES, S3_LOGGING_CONFIG

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
    Extrae el texto de un archivo PDF con cierre seguro de recursos.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")
    if not str(file_path).lower().endswith(tuple(SUPPORTED_PDF_TYPES)):
        raise ValueError(f"Tipo de archivo no soportado para PDF: {file_path}")

    text = ""
    if PYMUPDF_AVAILABLE:
        doc = None
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
        finally:
            if doc is not None:
                doc.close()
    elif PYPDF_AVAILABLE:
        # pypdf no requiere cierre explícito cuando se pasa ruta
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
        except Exception as e:
            raise Exception(f"Error procesando PDF con pypdf: {e}") from e
    else:
        raise Exception(
            "No hay una biblioteca de procesamiento de PDF disponible.\n"
            "Instala una con: pip install PyMuPDF o pip install pypdf"
        )

    limits = optimize_file_size_limits()
    max_chars = limits['max_text_chars']
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Texto truncado por límites de dispositivo]"
    return text


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


def log_to_s3(conversation: Dict[str, Any]):
    """
    Sube un artefacto de conversación a un bucket de S3/MinIO.

    Args:
        conversation: Diccionario con los datos de la conversación.
    """
    if not S3_LOGGING_CONFIG.get("enabled"):
        return

    # Validar configuración esencial
    required_keys = ["endpoint_url", "access_key", "secret_key", "bucket_name"]
    if not all(S3_LOGGING_CONFIG.get(key) for key in required_keys):
        print("Advertencia: Logging a S3 está habilitado pero la configuración es incompleta. No se guardará el log.")
        return

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_LOGGING_CONFIG["endpoint_url"],
            aws_access_key_id=S3_LOGGING_CONFIG["access_key"],
            aws_secret_access_key=S3_LOGGING_CONFIG["secret_key"]
        )
    except (NoCredentialsError, PartialCredentialsError):
        print("Advertencia: Credenciales de S3 no configuradas correctamente. No se guardará el log.")
        return
    except Exception as e:
        print(f"Advertencia: Error al inicializar el cliente de S3: {e}")
        return

    # Generar nombre del objeto
    conversation_id = conversation.get("id", "no-id")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_name = f"chats/{timestamp}_{conversation_id}.json"

    try:
        # Convertir diccionario a JSON string
        log_content = json.dumps(conversation, ensure_ascii=False, indent=2)

        # Subir el objeto
        s3_client.put_object(
            Bucket=S3_LOGGING_CONFIG["bucket_name"],
            Key=object_name,
            Body=log_content,
            ContentType='application/json'
        )
        print(f"\n[dim]📄 Log de conversación guardado en S3: {object_name}[/dim]")

    except ClientError as e:
        # Errores específicos del cliente de S3 (ej: bucket no encontrado, acceso denegado)
        error_code = e.response.get("Error", {}).get("Code")
        print(f"Advertencia: Error al subir log a S3 ({error_code}). Verifique la configuración del bucket y los permisos.")
    except Exception as e:
        print(f"Advertencia: Falla inesperada al subir log a S3: {e}")
