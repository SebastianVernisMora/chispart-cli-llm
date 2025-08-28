"""
Configuración para la aplicación Chispart-CLI-LLM
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de APIs disponibles - Solo Chispart/BlackboxAI
AVAILABLE_APIS = {
    "chispart": {
        "name": "Chispart (BlackboxAI)",
        "base_url": "https://api.blackbox.ai",
        "default_key_env": "BLACKBOX_API_KEY",
        "default_key": ""
    }
}

# API por defecto
DEFAULT_API = "chispart"

# Configuración de la API actual
def get_api_config(api_name=None):
    api_name = api_name or DEFAULT_API
    if api_name not in AVAILABLE_APIS:
        api_name = DEFAULT_API
    
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
    
    return result

# Modelos disponibles - Solo Chispart/BlackboxAI
AVAILABLE_MODELS = {
    "chispart": {
        "gpt-4": "blackboxai/openai/gpt-4",
        "gpt-4o": "blackboxai/openai/gpt-4o",
        "gpt-4o-mini": "blackboxai/openai/gpt-4o-mini",
        "gpt-4-turbo": "blackboxai/openai/gpt-4-turbo",
        "gpt-3.5-turbo": "blackboxai/openai/gpt-3.5-turbo",
        "claude-3.5-sonnet": "blackboxai/anthropic/claude-3.5-sonnet",
        "claude-3.5-haiku": "blackboxai/anthropic/claude-3.5-haiku",
        "claude-3-opus": "blackboxai/anthropic/claude-3-opus",
        "claude-3-sonnet": "blackboxai/anthropic/claude-3-sonnet",
        "claude-3-haiku": "blackboxai/anthropic/claude-3-haiku",
        "llama-3.1-405b": "blackboxai/meta-llama/llama-3.1-405b-instruct",
        "llama-3.1-70b": "blackboxai/meta-llama/llama-3.1-70b-instruct",
        "llama-3.1-8b": "blackboxai/meta-llama/llama-3.1-8b-instruct",
        "llama-3.3-70b": "blackboxai/meta-llama/llama-3.3-70b-instruct",
        "gemini-2.5-flash": "blackboxai/google/gemini-2.5-flash",
        "gemini-2.0-flash": "blackboxai/google/gemini-2.0-flash-001",
        "gemini-flash-1.5": "blackboxai/google/gemini-flash-1.5",
        "mixtral-8x7b": "blackboxai/mistralai/mixtral-8x7b-instruct",
        "mixtral-8x22b": "blackboxai/mistralai/mixtral-8x22b-instruct",
        "mistral-large": "blackboxai/mistralai/mistral-large-2411",
        "deepseek-r1": "blackboxai/deepseek/deepseek-r1",
        "deepseek-chat": "blackboxai/deepseek/deepseek-chat",
        "qwen-max": "blackboxai/qwen/qwen-max",
        "qwen-2.5-72b": "blackboxai/qwen/qwen-2.5-72b-instruct"
    }
}

# Modelo por defecto - Solo Chispart
DEFAULT_MODELS = {
    "chispart": "gpt-4"
}

def get_available_models(api_name=None):
    api_name = api_name or DEFAULT_API
    return AVAILABLE_MODELS.get(api_name, AVAILABLE_MODELS[DEFAULT_API])

def get_default_model(api_name=None):
    api_name = api_name or DEFAULT_API
    return DEFAULT_MODELS.get(api_name, DEFAULT_MODELS[DEFAULT_API])

# Configuración de timeouts (optimizado para Termux)
try:
    from termux_utils import get_mobile_optimized_timeouts, is_termux
    if is_termux():
        timeouts = get_mobile_optimized_timeouts()
        REQUEST_TIMEOUT = timeouts['total_timeout']
        CONNECT_TIMEOUT = timeouts['connect_timeout']
        READ_TIMEOUT = timeouts['read_timeout']
    else:
        REQUEST_TIMEOUT = 30
        CONNECT_TIMEOUT = 5
        READ_TIMEOUT = 30
except ImportError:
    REQUEST_TIMEOUT = 30
    CONNECT_TIMEOUT = 5
    READ_TIMEOUT = 30

# Tipos de archivo soportados
SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_PDF_TYPES = ['.pdf']

# APIs que soportan imágenes - Solo Chispart
VISION_SUPPORTED_APIS = ["chispart"]

# APIs que soportan PDFs - Solo Chispart
PDF_SUPPORTED_APIS = ["chispart"]

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
