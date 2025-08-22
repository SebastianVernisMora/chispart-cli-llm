"""
Utilidades específicas para Termux
Optimizaciones para el entorno móvil de Android
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any


def is_termux() -> bool:
    """Detecta si estamos ejecutando en Termux"""
    return os.path.exists('/data/data/com.termux') or 'com.termux' in os.environ.get('PREFIX', '')


def get_termux_temp_dir() -> str:
    """Obtiene el directorio temporal correcto para Termux"""
    if is_termux():
        # En Termux, usar el directorio home/tmp
        temp_dir = os.path.expanduser('~/tmp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    else:
        # En sistemas normales, usar /tmp
        return tempfile.gettempdir()


def get_safe_temp_path(filename: str) -> str:
    """Genera una ruta temporal segura para archivos"""
    temp_dir = get_termux_temp_dir()
    return os.path.join(temp_dir, filename)


def ensure_directory_exists(path: str) -> bool:
    """Asegura que un directorio existe, creándolo si es necesario"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except PermissionError:
        print(f"⚠️  No se pudo crear el directorio: {path}")
        return False
    except Exception as e:
        print(f"⚠️  Error creando directorio {path}: {str(e)}")
        return False


def get_termux_config_dir() -> str:
    """Obtiene el directorio de configuración para Termux"""
    if is_termux():
        config_dir = os.path.expanduser('~/.config/llm-cli')
    else:
        config_dir = os.path.expanduser('~/.config/llm-cli')
    
    ensure_directory_exists(config_dir)
    return config_dir


def get_optimized_console_width() -> int:
    """Obtiene un ancho de consola optimizado para dispositivos móviles"""
    try:
        # Intentar obtener el ancho real de la terminal
        columns = shutil.get_terminal_size().columns
        
        # En dispositivos móviles, limitar el ancho para mejor legibilidad
        if is_termux():
            # Para Termux, usar un máximo de 80 columnas para mejor legibilidad
            return min(columns, 80)
        else:
            return columns
    except:
        # Fallback para dispositivos móviles
        return 70 if is_termux() else 80


def check_termux_dependencies() -> Dict[str, bool]:
    """Verifica que las dependencias estén instaladas en Termux"""
    dependencies = {
        'requests': False,
        'click': False,
        'rich': False,
        'flask': False,
        'PIL': False,
        'fitz': False,  # PyMuPDF
        'dotenv': False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies


def print_termux_status():
    """Imprime el estado del sistema en Termux"""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console(width=get_optimized_console_width())
    
    # Información del sistema
    system_info = Table(title="🤖 Estado del Sistema")
    system_info.add_column("Componente", style="cyan")
    system_info.add_column("Estado", style="green")
    
    system_info.add_row("Entorno", "Termux" if is_termux() else "Sistema estándar")
    system_info.add_row("Python", f"{sys.version.split()[0]}")
    system_info.add_row("Directorio temporal", get_termux_temp_dir())
    system_info.add_row("Directorio config", get_termux_config_dir())
    system_info.add_row("Ancho de consola", str(get_optimized_console_width()))
    
    console.print(system_info)
    
    # Estado de dependencias
    deps = check_termux_dependencies()
    deps_table = Table(title="📦 Dependencias")
    deps_table.add_column("Paquete", style="cyan")
    deps_table.add_column("Estado", style="green")
    
    for dep, status in deps.items():
        status_text = "✅ Instalado" if status else "❌ Faltante"
        deps_table.add_row(dep, status_text)
    
    console.print(deps_table)
    
    # Consejos para Termux
    if is_termux():
        tips = Panel(
            "💡 [bold]Consejos para Termux:[/bold]\n\n"
            "• Usa 'pkg install python-pip' si pip no funciona\n"
            "• Para PDFs: 'pkg install clang make' antes de instalar PyMuPDF\n"
            "• Usa 'termux-setup-storage' para acceder a archivos del teléfono\n"
            "• El directorio ~/storage/shared/ contiene tus archivos del teléfono\n"
            "• Usa 'llm-web' para acceder desde el navegador del teléfono",
            title="🔧 Optimizaciones Termux",
            border_style="blue"
        )
        console.print(tips)


def get_mobile_optimized_timeouts() -> Dict[str, int]:
    """Obtiene timeouts optimizados para conexiones móviles"""
    if is_termux():
        return {
            'connect_timeout': 10,  # Más tiempo para conectar en móviles
            'read_timeout': 60,     # Más tiempo para leer respuestas
            'total_timeout': 120    # Timeout total más generoso
        }
    else:
        return {
            'connect_timeout': 5,
            'read_timeout': 30,
            'total_timeout': 60
        }


def optimize_file_size_limits() -> Dict[str, int]:
    """Obtiene límites de tamaño de archivo optimizados para móviles"""
    if is_termux():
        return {
            'max_image_size_mb': 10,  # Reducido para móviles
            'max_pdf_size_mb': 15,    # Reducido para móviles
            'max_text_chars': 50000   # Reducido para mejor rendimiento
        }
    else:
        return {
            'max_image_size_mb': 20,
            'max_pdf_size_mb': 20,
            'max_text_chars': 100000
        }


def setup_termux_environment():
    """Configura el entorno para Termux"""
    if not is_termux():
        return
    
    # Crear directorios necesarios
    ensure_directory_exists(get_termux_temp_dir())
    ensure_directory_exists(get_termux_config_dir())
    
    # Configurar variables de entorno específicas para Termux
    os.environ['TMPDIR'] = get_termux_temp_dir()
    
    # Configurar encoding para evitar problemas con caracteres especiales
    if 'PYTHONIOENCODING' not in os.environ:
        os.environ['PYTHONIOENCODING'] = 'utf-8'


def get_termux_storage_paths() -> Dict[str, str]:
    """Obtiene las rutas de almacenamiento de Termux"""
    base_path = os.path.expanduser('~/storage')
    
    paths = {
        'shared': os.path.join(base_path, 'shared'),
        'downloads': os.path.join(base_path, 'downloads'),
        'dcim': os.path.join(base_path, 'dcim'),
        'pictures': os.path.join(base_path, 'pictures'),
        'documents': os.path.join(base_path, 'shared', 'Documents')
    }
    
    # Verificar qué paths existen
    existing_paths = {}
    for name, path in paths.items():
        if os.path.exists(path):
            existing_paths[name] = path
    
    return existing_paths


def suggest_file_locations():
    """Sugiere ubicaciones de archivos para el usuario"""
    from rich.console import Console
    from rich.table import Table
    
    console = Console(width=get_optimized_console_width())
    
    if not is_termux():
        return
    
    storage_paths = get_termux_storage_paths()
    
    if not storage_paths:
        console.print("💡 Ejecuta 'termux-setup-storage' para acceder a los archivos de tu teléfono")
        return
    
    table = Table(title="📁 Ubicaciones de Archivos Sugeridas")
    table.add_column("Tipo", style="cyan")
    table.add_column("Ubicación", style="green")
    
    suggestions = {
        "Imágenes": storage_paths.get('pictures', storage_paths.get('dcim', '')),
        "Documentos": storage_paths.get('documents', ''),
        "Descargas": storage_paths.get('downloads', ''),
        "Archivos generales": storage_paths.get('shared', '')
    }
    
    for file_type, location in suggestions.items():
        if location:
            table.add_row(file_type, location)
    
    console.print(table)


# Configurar el entorno al importar el módulo
setup_termux_environment()