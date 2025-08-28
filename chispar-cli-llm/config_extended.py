"""
Configuración extendida para la aplicación Chispart-CLI-LLM
Incluye todos los modelos potentes disponibles en BlackboxAI
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de APIs disponibles - Múltiples APIs
AVAILABLE_APIS = {
    "chispart": {
        "name": "Chispart (BlackboxAI)",
        "base_url": "https://api.blackbox.ai",
        "default_key_env": "BLACKBOX_API_KEY",
        "default_key": ""
    },
    "qwen": {
        "name": "Qwen AI",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_key_env": "QWEN_API_KEY",
        "default_key": ""
    },
    "gemini": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_key_env": "GEMINI_API_KEY",
        "default_key": ""
    },
    "codestral": {
        "name": "Mistral Codestral",
        "base_url": "https://codestral.mistral.ai/v1",
        "default_key_env": "CODESTRAL_API_KEY",
        "default_key": ""
    }
}

# API por defecto
DEFAULT_API = "chispart"

# Cache para configuraciones de API (mejora rendimiento)
_api_config_cache = {}

# Configuración de la API actual
def get_api_config(api_name=None):
    """
    Obtiene la configuración para una API específica
    
    Args:
        api_name: Nombre de la API (opcional, usa DEFAULT_API si no se especifica)
        
    Returns:
        Diccionario con la configuración de la API
    """
    api_name = api_name or DEFAULT_API
    
    # Verificar si la API existe
    if api_name not in AVAILABLE_APIS:
        api_name = DEFAULT_API
    
    # Usar caché para mejorar rendimiento
    if api_name in _api_config_cache:
        # Verificar si estamos en modo test (pytest)
        if 'pytest' not in sys.modules:
            return _api_config_cache[api_name]
    
    config = AVAILABLE_APIS[api_name]
    
    # Compatibilidad retro: permitir BLACKBOX_API_KEY o CHISPART_API_KEY
    if api_name == "chispart":
        api_key = os.getenv("CHISPART_API_KEY") or os.getenv("BLACKBOX_API_KEY") or config.get("default_key", "")
    else:
        api_key = os.getenv(config["default_key_env"], config.get("default_key", ""))

    # Añadir configuración de timeouts optimizada
    result = {
        "name": config["name"],
        "base_url": config["base_url"],
        "api_key": api_key,
        "timeout": REQUEST_TIMEOUT,
        "connect_timeout": CONNECT_TIMEOUT,
        "read_timeout": READ_TIMEOUT
    }
    
    # Guardar en caché para futuras llamadas (excepto en tests)
    if 'pytest' not in sys.modules:
        _api_config_cache[api_name] = result
    
    return result

# Modelos disponibles - Todos los modelos potentes de BlackboxAI
AVAILABLE_MODELS = {
    "chispart": {
        # OpenAI Models (más potentes)
        "gpt-4": "blackboxai/openai/gpt-4",
        "gpt-4o": "blackboxai/openai/gpt-4o",
        "gpt-4o-mini": "blackboxai/openai/gpt-4o-mini",
        "gpt-4-turbo": "blackboxai/openai/gpt-4-turbo",
        "gpt-4-turbo-preview": "blackboxai/openai/gpt-4-turbo-preview",
        "gpt-4-vision": "blackboxai/openai/gpt-4-vision-preview",
        "gpt-3.5-turbo": "blackboxai/openai/gpt-3.5-turbo",
        "gpt-3.5-turbo-16k": "blackboxai/openai/gpt-3.5-turbo-16k",
        
        # Anthropic Claude (más potentes)
        "claude-3.5-sonnet": "blackboxai/anthropic/claude-3.5-sonnet",
        "claude-3.5-haiku": "blackboxai/anthropic/claude-3.5-haiku",
        "claude-3-opus": "blackboxai/anthropic/claude-3-opus",
        "claude-3-sonnet": "blackboxai/anthropic/claude-3-sonnet",
        "claude-3-haiku": "blackboxai/anthropic/claude-3-haiku",
        "claude-2.1": "blackboxai/anthropic/claude-2.1",
        "claude-2": "blackboxai/anthropic/claude-2.0",
        
        # Meta Llama (más potentes)
        "llama-3.1-405b": "blackboxai/meta-llama/llama-3.1-405b-instruct",
        "llama-3.1-70b": "blackboxai/meta-llama/llama-3.1-70b-instruct",
        "llama-3.1-8b": "blackboxai/meta-llama/llama-3.1-8b-instruct",
        "llama-3.3-70b": "blackboxai/meta-llama/llama-3.3-70b-instruct",
        "llama-3.2-90b": "blackboxai/meta-llama/llama-3.2-90b-instruct",
        "llama-3.2-11b": "blackboxai/meta-llama/llama-3.2-11b-instruct",
        "llama-3.2-3b": "blackboxai/meta-llama/llama-3.2-3b-instruct",
        "llama-3.2-1b": "blackboxai/meta-llama/llama-3.2-1b-instruct",
        
        # Google Gemini (más potentes)
        "gemini-2.5-flash": "blackboxai/google/gemini-2.5-flash",
        "gemini-2.0-flash": "blackboxai/google/gemini-2.0-flash-001",
        "gemini-flash-1.5": "blackboxai/google/gemini-flash-1.5",
        "gemini-pro": "blackboxai/google/gemini-pro",
        "gemini-pro-vision": "blackboxai/google/gemini-pro-vision",
        
        # Mistral (más potentes)
        "mixtral-8x7b": "blackboxai/mistralai/mixtral-8x7b-instruct",
        "mixtral-8x22b": "blackboxai/mistralai/mixtral-8x22b-instruct",
        "mistral-large": "blackboxai/mistralai/mistral-large-2411",
        "mistral-medium": "blackboxai/mistralai/mistral-medium",
        "mistral-small": "blackboxai/mistralai/mistral-small",
        "mistral-7b": "blackboxai/mistralai/mistral-7b-instruct",
        
        # DeepSeek (más potentes)
        "deepseek-r1": "blackboxai/deepseek/deepseek-r1",
        "deepseek-chat": "blackboxai/deepseek/deepseek-chat",
        "deepseek-coder": "blackboxai/deepseek/deepseek-coder",
        "deepseek-math": "blackboxai/deepseek/deepseek-math",
        
        # Qwen (más potentes)
        "qwen-max": "blackboxai/qwen/qwen-max",
        "qwen-2.5-72b": "blackboxai/qwen/qwen-2.5-72b-instruct",
        "qwen-2.5-32b": "blackboxai/qwen/qwen-2.5-32b-instruct",
        "qwen-2.5-14b": "blackboxai/qwen/qwen-2.5-14b-instruct",
        "qwen-2.5-7b": "blackboxai/qwen/qwen-2.5-7b-instruct",
        "qwen-2.5-coder": "blackboxai/qwen/qwen-2.5-coder-32b-instruct",
        
        # Otros modelos potentes
        "yi-large": "blackboxai/01-ai/yi-large",
        "yi-34b": "blackboxai/01-ai/yi-34b-chat",
        "command-r-plus": "blackboxai/cohere/command-r-plus",
        "command-r": "blackboxai/cohere/command-r",
        "dbrx": "blackboxai/databricks/dbrx-instruct",
        "phi-3-medium": "blackboxai/microsoft/phi-3-medium-4k-instruct",
        "phi-3-mini": "blackboxai/microsoft/phi-3-mini-4k-instruct",
        
        # Modelos especializados en código
        "codellama-70b": "blackboxai/meta-llama/codellama-70b-instruct",
        "codellama-34b": "blackboxai/meta-llama/codellama-34b-instruct",
        "codellama-13b": "blackboxai/meta-llama/codellama-13b-instruct",
        "codellama-7b": "blackboxai/meta-llama/codellama-7b-instruct",
        "starcoder2-15b": "blackboxai/bigcode/starcoder2-15b",
        "starcoder2-7b": "blackboxai/bigcode/starcoder2-7b",
        
        # Modelos matemáticos y científicos
        "mathstral-7b": "blackboxai/mistralai/mathstral-7b-v0.1",
        "wizardmath-70b": "blackboxai/wizardlm/wizardmath-70b-v1.0",
        "wizardcoder-34b": "blackboxai/wizardlm/wizardcoder-34b-v1.0"
    },
    "qwen": {
        # Modelos Qwen nativos
        "qwen-turbo": "qwen-turbo",
        "qwen-plus": "qwen-plus",
        "qwen-max": "qwen-max",
        "qwen-max-longcontext": "qwen-max-longcontext",
        "qwen2.5-72b-instruct": "qwen2.5-72b-instruct",
        "qwen2.5-32b-instruct": "qwen2.5-32b-instruct",
        "qwen2.5-14b-instruct": "qwen2.5-14b-instruct",
        "qwen2.5-7b-instruct": "qwen2.5-7b-instruct",
        "qwen2.5-coder-32b-instruct": "qwen2.5-coder-32b-instruct",
        "qwen2.5-coder-14b-instruct": "qwen2.5-coder-14b-instruct",
        "qwen2.5-coder-7b-instruct": "qwen2.5-coder-7b-instruct",
        "qwen2.5-math-72b-instruct": "qwen2.5-math-72b-instruct",
        "qwen2.5-math-7b-instruct": "qwen2.5-math-7b-instruct"
    },
    "gemini": {
        # Modelos Google Gemini nativos
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash",
        "gemini-1.0-pro": "gemini-1.0-pro",
        "gemini-pro": "gemini-pro",
        "gemini-pro-vision": "gemini-pro-vision",
        "gemini-1.5-pro-latest": "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest": "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b": "gemini-1.5-flash-8b"
    },
    "codestral": {
        # Modelos Mistral Codestral especializados en código
        "codestral-latest": "codestral-latest",
        "codestral-2405": "codestral-2405",
        "codestral-mamba-latest": "codestral-mamba-latest",
        "mistral-large-latest": "mistral-large-latest",
        "mistral-small-latest": "mistral-small-latest"
    }
}

# Modelo por defecto para cada API
DEFAULT_MODELS = {
    "chispart": "gpt-4",
    "qwen": "qwen-max",
    "gemini": "gemini-1.5-pro",
    "codestral": "codestral-latest"
}

def get_available_models(api_name=None):
    """
    Obtiene los modelos disponibles para una API específica
    
    Args:
        api_name: Nombre de la API (opcional, usa DEFAULT_API si no se especifica)
        
    Returns:
        Diccionario con los modelos disponibles
    """
    api_name = api_name or DEFAULT_API
    
    # Verificar que la API existe en AVAILABLE_MODELS
    if api_name not in AVAILABLE_MODELS:
        # Si la API no existe, usar la API por defecto
        api_name = DEFAULT_API
    
    # Verificar que la API por defecto existe (seguridad adicional)
    if api_name not in AVAILABLE_MODELS:
        # Si ni siquiera la API por defecto existe, retornar un diccionario vacío
        return {}
    
    return AVAILABLE_MODELS[api_name]

def get_default_model(api_name=None):
    api_name = api_name or DEFAULT_API
    return DEFAULT_MODELS.get(api_name, DEFAULT_MODELS[DEFAULT_API])

# Importar funciones de termux_utils con manejo de errores mejorado
try:
    from termux_utils import get_mobile_optimized_timeouts, is_termux
    TERMUX_UTILS_AVAILABLE = True
except ImportError:
    TERMUX_UTILS_AVAILABLE = False
    
    # Funciones de fallback si termux_utils no está disponible
    def is_termux():
        return False
    
    def get_mobile_optimized_timeouts():
        return {
            'connect_timeout': 10,
            'read_timeout': 60,
            'total_timeout': 120
        }

def _get_timeouts():
    """Función para obtener timeouts dinámicamente"""
    if is_termux():
        timeouts = get_mobile_optimized_timeouts()
        return {
            'REQUEST_TIMEOUT': timeouts['total_timeout'],  # 120 para tests
            'CONNECT_TIMEOUT': timeouts['connect_timeout'],
            'READ_TIMEOUT': timeouts['read_timeout']
        }
    else:
        return {
            'REQUEST_TIMEOUT': 30,
            'CONNECT_TIMEOUT': 5,
            'READ_TIMEOUT': 30
        }

# Configuración de timeouts (optimizado para Termux)
_timeout_config = _get_timeouts()
REQUEST_TIMEOUT = _timeout_config['REQUEST_TIMEOUT']
CONNECT_TIMEOUT = _timeout_config['CONNECT_TIMEOUT']
READ_TIMEOUT = _timeout_config['READ_TIMEOUT']

# Tipos de archivo soportados
SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_PDF_TYPES = ['.pdf']

# APIs que soportan imágenes
VISION_SUPPORTED_APIS = ["chispart", "gemini", "qwen"]

# APIs que soportan PDFs (sin validación estricta)
PDF_SUPPORTED_APIS = ["chispart", "gemini", "qwen", "codestral"]

# Configuración específica para Termux
TERMUX_OPTIMIZATIONS = {
    "max_image_size_mb": 10,  # Reducido para móviles
    "max_pdf_size_mb": 15,    # Reducido para móviles
    "max_text_chars": 50000,  # Reducido para mejor rendimiento
    "console_width": 70,      # Optimizado para pantallas pequeñas
    "enable_rich_formatting": True,
    "use_compact_tables": True
}

# Configuración de red optimizada para móviles
MOBILE_NETWORK_CONFIG = {
    "retry_attempts": 3,
    "retry_delay": 2,
    "chunk_size": 1024,  # Tamaño de chunk más pequeño para conexiones lentas
    "stream_timeout": 120  # Timeout más largo para streaming
}

# Configuración de logging en S3/MinIO
S3_LOGGING_CONFIG = {
    "enabled": os.getenv("S3_LOGGING_ENABLED", "false").lower() == "true",
    "endpoint_url": os.getenv("S3_ENDPOINT_URL"),
    "access_key": os.getenv("S3_ACCESS_KEY_ID"),
    "secret_key": os.getenv("S3_SECRET_ACCESS_KEY"),
    "bucket_name": os.getenv("S3_BUCKET_NAME")
}

# Configuración de seguridad
PLAN_BASED_SECURITY_CONFIG = {
    "free": {
        "whitelist_enabled": True,
        "allowed_commands": [
            "ls", "pwd", "cd", "cat", "grep", "find", "which", "echo", "date", "whoami",
            "python", "python3", "node", "pip"
        ],
        "blocked_commands": [
            "sudo", "su", "passwd", "useradd", "userdel", "usermod", "systemctl", "service",
            "mount", "umount", "fdisk", "mkfs", "iptables", "ufw", "firewall-cmd", "setenforce",
            "crontab", "at", "batch", "nc", "netcat", "nmap", "tcpdump", "wireshark", "rm -rf"
        ],
        "require_confirmation": ["rm", "rmdir", "mv", "cp"]
    },
    "basic": {
        "whitelist_enabled": True,
        "allowed_commands": [
            "ls", "pwd", "cd", "cat", "grep", "find", "which", "echo", "date", "whoami",
            "python", "python3", "node", "pip", "git", "npm", "yarn",
            "mkdir", "rmdir", "touch", "cp", "mv", "rm"
        ],
        "blocked_commands": [
            "sudo", "su", "passwd", "useradd", "userdel", "usermod", "systemctl", "service",
            "mount", "umount", "fdisk", "mkfs", "iptables", "ufw", "firewall-cmd", "setenforce",
            "crontab", "at", "batch", "nc", "netcat", "nmap", "tcpdump", "wireshark", "rm -rf"
        ],
        "require_confirmation": ["rm", "rmdir", "mv", "cp", "git push"]
    },
    "pro": {
        "whitelist_enabled": True,
        "allowed_commands": [
            "ls", "pwd", "cd", "cat", "grep", "find", "which", "echo", "date", "whoami",
            "python", "python3", "node", "pip", "git", "npm", "yarn", "docker", "kubectl",
            "mkdir", "rmdir", "touch", "cp", "mv", "rm", "chmod", "chown",
            "curl", "wget", "ping", "ssh", "scp",
            "vim", "nano", "code", "less", "more", "head", "tail", "sort", "uniq", "wc"
        ],
        "blocked_commands": [
            "sudo", "su", "passwd", "useradd", "userdel", "usermod", "systemctl", "service",
            "mount", "umount", "fdisk", "mkfs", "iptables", "ufw", "firewall-cmd", "setenforce",
            "crontab", "at", "batch", "nc", "netcat", "nmap", "tcpdump", "wireshark", "rm -rf"
        ],
        "require_confirmation": ["rm", "rmdir", "mv", "cp", "chmod", "chown", "git push", "docker run"]
    }
}

def get_security_config(plan: str) -> dict:
    """
    Obtiene la configuración de seguridad para un plan específico.

    Args:
        plan: El plan del usuario (free, basic, pro)

    Returns:
        Diccionario con la configuración de seguridad.
    """
    return PLAN_BASED_SECURITY_CONFIG.get(plan, PLAN_BASED_SECURITY_CONFIG["free"])

# Configuración de split chat
SPLIT_CHAT_CONFIG = {
    "base_port": 5001,  # Puerto base para split chats
    "max_splits": 5,    # Máximo número de splits simultáneos
    "auto_merge_timeout": 3600,  # Timeout para auto-merge (1 hora)
    "context_limit": 10000,  # Límite de caracteres para contexto
}
