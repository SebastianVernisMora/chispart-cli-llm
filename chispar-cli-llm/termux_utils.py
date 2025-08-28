"""
Utilidades de compatibilidad para Termux (versión simplificada para escritorio)
Proporciona funciones de fallback sin dependencias obligatorias de Termux
"""
import os
import sys
import shutil
from typing import Dict, Optional


def is_termux() -> bool:
    """
    Detecta si estamos ejecutando en Termux
    
    Returns:
        False por defecto en entorno de escritorio
    """
    # Verificar variables de entorno específicas de Termux
    termux_indicators = [
        os.environ.get('PREFIX', '').startswith('/data/data/com.termux'),
        os.environ.get('TERMUX_VERSION') is not None,
        os.path.exists('/data/data/com.termux'),
        'com.termux' in os.environ.get('PREFIX', ''),
        'termux' in os.environ.get('HOME', '').lower()
    ]
    
    return any(termux_indicators)


def get_mobile_optimized_timeouts() -> Dict[str, int]:
    """
    Obtiene timeouts optimizados para conexiones móviles
    
    Returns:
        Diccionario con configuración de timeouts
    """
    if is_termux():
        # Timeouts más largos para conexiones móviles
        return {
            'connect_timeout': 15,  # Tiempo para establecer conexión
            'read_timeout': 120,    # Tiempo para leer respuesta
            'total_timeout': 180    # Tiempo total máximo
        }
    else:
        # Timeouts estándar para desktop
        return {
            'connect_timeout': 10,
            'read_timeout': 60,
            'total_timeout': 120
        }


def get_optimized_console_width() -> int:
    """
    Obtiene el ancho de consola optimizado para el dispositivo
    
    Returns:
        Ancho de consola recomendado
    """
    try:
        # Intentar obtener el ancho real del terminal
        columns = shutil.get_terminal_size().columns
        
        if is_termux():
            # En Termux, limitar a un máximo para mejor legibilidad
            return min(columns, 80)
        else:
            # En desktop, usar el ancho completo
            return columns
            
    except Exception:
        # Fallback
        return 70 if is_termux() else 80


def get_safe_temp_path(filename: str) -> str:
    """
    Obtiene una ruta temporal segura para el archivo
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Ruta temporal segura
    """
    import tempfile
    
    if is_termux():
        # En Termux, usar el directorio home/tmp
        temp_dir = os.path.join(os.environ.get('HOME', '/data/data/com.termux/files/home'), '.tmp')
        os.makedirs(temp_dir, exist_ok=True)
        return os.path.join(temp_dir, filename)
    else:
        # En sistemas normales, usar tempfile
        return os.path.join(tempfile.gettempdir(), filename)


def ensure_directory_exists(directory: str) -> bool:
    """
    Asegura que un directorio existe
    
    Args:
        directory: Ruta del directorio
        
    Returns:
        True si el directorio existe o se creó exitosamente
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception:
        return False


def optimize_file_size_limits() -> Dict[str, int]:
    """
    Obtiene límites de archivo optimizados
    
    Returns:
        Diccionario con límites de archivo
    """
    if is_termux():
        return {
            'max_image_size_mb': 10,    # Máximo 10MB para imágenes
            'max_pdf_size_mb': 15,      # Máximo 15MB para PDFs
            'max_text_chars': 50000,    # Máximo 50k caracteres de texto
            'max_upload_size_mb': 20    # Máximo 20MB para uploads
        }
    else:
        return {
            'max_image_size_mb': 50,    # Máximo 50MB para imágenes
            'max_pdf_size_mb': 100,     # Máximo 100MB para PDFs
            'max_text_chars': 200000,   # Máximo 200k caracteres de texto
            'max_upload_size_mb': 100   # Máximo 100MB para uploads
        }


def get_termux_info() -> Dict[str, str]:
    """
    Obtiene información del entorno (compatible con desktop)
    
    Returns:
        Diccionario con información del entorno
    """
    info = {
        'is_termux': str(is_termux()),
        'platform': 'termux' if is_termux() else 'desktop',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'home': os.environ.get('HOME', 'unknown'),
        'shell': os.environ.get('SHELL', 'unknown')
    }
    
    if hasattr(os, 'uname'):
        info['architecture'] = os.uname().machine
    
    return info


def check_termux_dependencies() -> Dict[str, bool]:
    """
    Verifica dependencias (versión simplificada para desktop)
    
    Returns:
        Diccionario con estado de dependencias
    """
    dependencies = {
        'python': True,  # Asumimos que Python está disponible
        'git': False,
        'curl': False,
        'wget': False
    }
    
    # Verificar comandos básicos
    for cmd in ['git', 'curl', 'wget']:
        try:
            result = os.system(f'which {cmd} > /dev/null 2>&1')
            dependencies[cmd] = (result == 0)
        except Exception:
            dependencies[cmd] = False
    
    return dependencies


# Funciones de compatibilidad adicionales
def print_termux_status():
    """Imprime el estado del entorno (compatible con desktop)"""
    info = get_termux_info()
    print(f"🖥️  Plataforma: {info['platform']}")
    print(f"🐍 Python: {info['python_version']}")
    if info.get('architecture'):
        print(f"🏗️  Arquitectura: {info['architecture']}")


def setup_termux_environment() -> Dict[str, str]:
    """
    Configuración del entorno (versión simplificada)
    
    Returns:
        Diccionario con resultados de configuración
    """
    results = {
        'status': 'desktop_mode',
        'platform': 'desktop',
        'optimizations_applied': 'false'
    }
    
    if is_termux():
        results.update({
            'status': 'termux_detected',
            'platform': 'termux',
            'optimizations_applied': 'true'
        })
    
    return results
