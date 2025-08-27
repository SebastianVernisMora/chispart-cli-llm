"""
Utilidades específicas para Termux
Optimizaciones y configuraciones para el entorno móvil Android
"""
import os
import sys
import shutil
from typing import Dict, Optional, Tuple
from pathlib import Path

def is_termux() -> bool:
    """
    Detecta si estamos ejecutando en Termux
    
    Returns:
        True si estamos en Termux
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

def get_termux_info() -> Dict[str, str]:
    """
    Obtiene información del entorno Termux
    
    Returns:
        Diccionario con información de Termux
    """
    info = {
        'is_termux': str(is_termux()),
        'termux_version': os.environ.get('TERMUX_VERSION', 'unknown'),
        'prefix': os.environ.get('PREFIX', 'unknown'),
        'home': os.environ.get('HOME', 'unknown'),
        'shell': os.environ.get('SHELL', 'unknown'),
        'android_root': os.environ.get('ANDROID_ROOT', 'unknown'),
        'android_data': os.environ.get('ANDROID_DATA', 'unknown')
    }
    
    # Información adicional si estamos en Termux
    if is_termux():
        try:
            # Versión de Android
            if os.path.exists('/system/build.prop'):
                with open('/system/build.prop', 'r') as f:
                    for line in f:
                        if 'ro.build.version.release' in line:
                            info['android_version'] = line.split('=')[1].strip()
                            break
            
            # Arquitectura del dispositivo
            info['architecture'] = os.uname().machine
            
            # Espacio disponible
            statvfs = os.statvfs(os.environ.get('HOME', '/'))
            available_bytes = statvfs.f_bavail * statvfs.f_frsize
            info['available_space_mb'] = str(int(available_bytes / (1024 * 1024)))
            
        except Exception:
            pass
    
    return info

def get_termux_config_dir() -> str:
    """
    Obtiene el directorio de configuración para Termux
    
    Returns:
        Ruta al directorio de configuración
    """
    if is_termux():
        # En Termux, usar el directorio home
        config_dir = os.path.join(os.environ.get('HOME', '/data/data/com.termux/files/home'), '.config', 'chispart-mobile')
    else:
        # En sistemas normales
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'chispart-mobile')
    
    # Crear directorio si no existe
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_termux_temp_dir() -> str:
    """
    Obtiene el directorio temporal para Termux
    
    Returns:
        Ruta al directorio temporal
    """
    if is_termux():
        # En Termux, usar un directorio temporal en el home
        temp_dir = os.path.join(os.environ.get('HOME', '/data/data/com.termux/files/home'), '.tmp')
    else:
        # En sistemas normales, usar /tmp
        temp_dir = '/tmp'
    
    # Crear directorio si no existe
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

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

def get_mobile_file_limits() -> Dict[str, int]:
    """
    Obtiene límites de archivo optimizados para móviles
    
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

def check_termux_packages() -> Dict[str, bool]:
    """
    Verifica qué paquetes de Termux están instalados
    
    Returns:
        Diccionario con estado de paquetes
    """
    packages = {
        'python': False,
        'git': False,
        'curl': False,
        'wget': False,
        'openssh': False,
        'nodejs': False,
        'vim': False,
        'nano': False
    }
    
    if not is_termux():
        return packages
    
    # Verificar cada paquete
    for package in packages.keys():
        try:
            # Verificar si el comando existe
            result = os.system(f'which {package} > /dev/null 2>&1')
            packages[package] = (result == 0)
        except Exception:
            packages[package] = False
    
    return packages

def get_termux_storage_info() -> Dict[str, str]:
    """
    Obtiene información de almacenamiento en Termux
    
    Returns:
        Diccionario con información de almacenamiento
    """
    info = {}
    
    if not is_termux():
        return info
    
    try:
        # Información del directorio home
        home_dir = os.environ.get('HOME', '/data/data/com.termux/files/home')
        if os.path.exists(home_dir):
            statvfs = os.statvfs(home_dir)
            total_bytes = statvfs.f_blocks * statvfs.f_frsize
            available_bytes = statvfs.f_bavail * statvfs.f_frsize
            used_bytes = total_bytes - available_bytes
            
            info.update({
                'home_total_mb': str(int(total_bytes / (1024 * 1024))),
                'home_used_mb': str(int(used_bytes / (1024 * 1024))),
                'home_available_mb': str(int(available_bytes / (1024 * 1024))),
                'home_usage_percent': str(int((used_bytes / total_bytes) * 100))
            })
        
        # Verificar acceso a almacenamiento compartido
        shared_storage = '/storage/emulated/0'
        if os.path.exists(shared_storage):
            info['shared_storage_accessible'] = 'true'
        else:
            info['shared_storage_accessible'] = 'false'
        
        # Verificar permisos de almacenamiento
        try:
            test_file = os.path.join(home_dir, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            info['write_permissions'] = 'true'
        except Exception:
            info['write_permissions'] = 'false'
            
    except Exception as e:
        info['error'] = str(e)
    
    return info

def setup_termux_environment() -> Dict[str, str]:
    """
    Configura el entorno Termux para Chispart Mobile
    
    Returns:
        Diccionario con resultados de la configuración
    """
    results = {}
    
    if not is_termux():
        results['status'] = 'not_termux'
        return results
    
    try:
        # Crear directorios necesarios
        config_dir = get_termux_config_dir()
        temp_dir = get_termux_temp_dir()
        
        results['config_dir'] = config_dir
        results['temp_dir'] = temp_dir
        
        # Verificar permisos de escritura
        try:
            test_file = os.path.join(config_dir, '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            results['write_permissions'] = 'ok'
        except Exception as e:
            results['write_permissions'] = f'error: {e}'
        
        # Configurar variables de entorno si es necesario
        env_vars = {
            'CHISPART_MOBILE_CONFIG': config_dir,
            'CHISPART_MOBILE_TEMP': temp_dir,
            'CHISPART_MOBILE_PLATFORM': 'termux'
        }
        
        for var, value in env_vars.items():
            os.environ[var] = value
        
        results['env_vars'] = 'configured'
        results['status'] = 'success'
        
    except Exception as e:
        results['status'] = 'error'
        results['error'] = str(e)
    
    return results

def get_network_info() -> Dict[str, str]:
    """
    Obtiene información de red en Termux
    
    Returns:
        Diccionario con información de red
    """
    info = {}
    
    try:
        # Verificar conectividad básica
        import socket
        
        # Test de conectividad a Google DNS
        try:
            socket.create_connection(('8.8.8.8', 53), timeout=5)
            info['internet_connectivity'] = 'true'
        except Exception:
            info['internet_connectivity'] = 'false'
        
        # Obtener IP local
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            info['local_ip'] = s.getsockname()[0]
            s.close()
        except Exception:
            info['local_ip'] = 'unknown'
        
        # Verificar si estamos en WiFi o datos móviles (solo en Termux)
        if is_termux():
            try:
                # Intentar ejecutar comando termux-api si está disponible
                result = os.popen('termux-wifi-connectioninfo 2>/dev/null').read()
                if result.strip():
                    info['connection_type'] = 'wifi'
                    info['wifi_info'] = result.strip()
                else:
                    info['connection_type'] = 'mobile_data'
            except Exception:
                info['connection_type'] = 'unknown'
        
    except Exception as e:
        info['error'] = str(e)
    
    return info

def optimize_for_mobile() -> Dict[str, any]:
    """
    Aplica optimizaciones específicas para dispositivos móviles
    
    Returns:
        Diccionario con configuraciones aplicadas
    """
    optimizations = {}
    
    if is_termux():
        # Configuraciones específicas para Termux
        optimizations.update({
            'timeouts': get_mobile_optimized_timeouts(),
            'file_limits': get_mobile_file_limits(),
            'console_width': get_optimized_console_width(),
            'temp_dir': get_termux_temp_dir(),
            'config_dir': get_termux_config_dir()
        })
        
        # Configurar variables de entorno
        os.environ['CHISPART_MOBILE_OPTIMIZED'] = 'true'
        os.environ['CHISPART_MOBILE_PLATFORM'] = 'termux'
        
        # Configuraciones de red
        network_config = {
            'retry_attempts': 3,
            'retry_delay': 2,
            'chunk_size': 1024,
            'stream_timeout': 120
        }
        optimizations['network'] = network_config
        
    else:
        # Configuraciones para desktop
        optimizations.update({
            'timeouts': get_mobile_optimized_timeouts(),
            'file_limits': get_mobile_file_limits(),
            'console_width': get_optimized_console_width()
        })
        
        os.environ['CHISPART_MOBILE_PLATFORM'] = 'desktop'
    
    return optimizations

def check_termux_api() -> Dict[str, bool]:
    """
    Verifica disponibilidad de Termux API
    
    Returns:
        Diccionario con APIs disponibles
    """
    apis = {
        'termux-battery-status': False,
        'termux-wifi-connectioninfo': False,
        'termux-notification': False,
        'termux-toast': False,
        'termux-vibrate': False,
        'termux-wake-lock': False,
        'termux-storage-get': False
    }
    
    if not is_termux():
        return apis
    
    # Verificar cada API
    for api in apis.keys():
        try:
            result = os.system(f'which {api} > /dev/null 2>&1')
            apis[api] = (result == 0)
        except Exception:
            apis[api] = False
    
    return apis

def get_device_capabilities() -> Dict[str, any]:
    """
    Obtiene capacidades del dispositivo
    
    Returns:
        Diccionario con capacidades del dispositivo
    """
    capabilities = {
        'platform': 'termux' if is_termux() else 'desktop',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'architecture': os.uname().machine if hasattr(os, 'uname') else 'unknown'
    }
    
    if is_termux():
        capabilities.update({
            'termux_info': get_termux_info(),
            'termux_packages': check_termux_packages(),
            'termux_apis': check_termux_api(),
            'storage_info': get_termux_storage_info(),
            'network_info': get_network_info()
        })
    
    return capabilities

# Función de inicialización automática
def auto_setup():
    """
    Configuración automática al importar el módulo
    """
    if is_termux():
        # Aplicar optimizaciones automáticamente
        optimize_for_mobile()
        
        # Configurar entorno si es la primera vez
        setup_results = setup_termux_environment()
        
        # Mostrar información de configuración si hay errores
        if setup_results.get('status') != 'success':
            print(f"⚠️  Advertencia en configuración Termux: {setup_results}")

# Ejecutar configuración automática al importar
auto_setup()
