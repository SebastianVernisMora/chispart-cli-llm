"""
Configuración para la aplicación CLI de BlackboxAI
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de APIs disponibles
AVAILABLE_APIS = {
    "blackbox": {
        "name": "BlackboxAI",
        "base_url": "https://api.blackbox.ai",
        "default_key_env": "BLACKBOX_API_KEY",
        "default_key": ""
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_key_env": "OPENAI_API_KEY",
        "default_key": ""
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com",
        "default_key_env": "ANTHROPIC_API_KEY",
        "default_key": ""
    },
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "default_key_env": "GROQ_API_KEY",
        "default_key": ""
    },
    "together": {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "default_key_env": "TOGETHER_API_KEY",
        "default_key": ""
    }
}

# API por defecto
DEFAULT_API = "blackbox"

# Configuración de la API actual
def get_api_config(api_name=None):
    api_name = api_name or DEFAULT_API
    if api_name not in AVAILABLE_APIS:
        api_name = DEFAULT_API
    
    config = AVAILABLE_APIS[api_name]
    api_key = os.getenv(config["default_key_env"], config["default_key"])
    
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

# Modelos disponibles por API (actualizados con modelos reales)
AVAILABLE_MODELS = {
    "blackbox": {
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
    },
    "openai": {
        "gpt-4": "gpt-4",
        "gpt-4-turbo": "gpt-4-turbo-preview",
        "gpt-4-vision": "gpt-4-vision-preview",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k": "gpt-3.5-turbo-16k"
    },
    "anthropic": {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-2.1": "claude-2.1",
        "claude-2": "claude-2.0"
    },
    "groq": {
        "llama-3.1-70b": "llama-3.1-70b-versatile",
        "llama-3.1-8b": "llama-3.1-8b-instant",
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gemma-7b": "gemma-7b-it"
    },
    "together": {
        "llama-3.1-70b": "meta-llama/Llama-3.1-70B-Instruct-Turbo",
        "llama-3.1-8b": "meta-llama/Llama-3.1-8B-Instruct-Turbo",
        "mixtral-8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "qwen-2-72b": "Qwen/Qwen2-72B-Instruct"
    }
}

# Modelo por defecto por API
DEFAULT_MODELS = {
    "blackbox": "gpt-4",
    "openai": "gpt-4",
    "anthropic": "claude-3-sonnet",
    "groq": "llama-3.1-70b",
    "together": "llama-3.1-70b"
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

# APIs que soportan imágenes
VISION_SUPPORTED_APIS = ["blackbox", "openai", "anthropic"]

# APIs que soportan PDFs
PDF_SUPPORTED_APIS = ["blackbox", "openai"]

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
