"""
Configuración extendida para Chispart Mobile
Integra la configuración avanzada de chispar-cli-llm con 100+ modelos de IA
"""
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de APIs disponibles - Múltiples APIs
AVAILABLE_APIS = {
    "blackbox": {
        "name": "Blackbox AI",
        "base_url": "https://api.blackbox.ai",
        "default_key_env": "BLACKBOX_API_KEY",
        "supports_vision": True,
        "supports_pdf": True
    },
    "chispart": {
        "name": "Chispart (BlackboxAI)",
        "base_url": "https://api.blackbox.ai",
        "default_key_env": "BLACKBOX_API_KEY",
        "supports_vision": True,
        "supports_pdf": True
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_key_env": "OPENAI_API_KEY",
        "supports_vision": True,
        "supports_pdf": True
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com",
        "default_key_env": "ANTHROPIC_API_KEY",
        "supports_vision": True,
        "supports_pdf": False
    },
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "default_key_env": "GROQ_API_KEY",
        "supports_vision": False,
        "supports_pdf": False
    },
    "together": {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "default_key_env": "TOGETHER_API_KEY",
        "supports_vision": False,
        "supports_pdf": False
    },
    "qwen": {
        "name": "Qwen AI",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_key_env": "QWEN_API_KEY",
        "supports_vision": True,
        "supports_pdf": True
    },
    "gemini": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_key_env": "GEMINI_API_KEY",
        "supports_vision": True,
        "supports_pdf": True
    },
    "codestral": {
        "name": "Mistral Codestral",
        "base_url": "https://codestral.mistral.ai/v1",
        "default_key_env": "CODESTRAL_API_KEY",
        "supports_vision": False,
        "supports_pdf": True
    }
}

# API por defecto
DEFAULT_API = "blackbox"

# Modelos disponibles - Todos los modelos potentes integrados
AVAILABLE_MODELS = {
    "blackbox": {
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
    "chispart": {
        # Alias para blackbox (compatibilidad)
        "gpt-4": "blackboxai/openai/gpt-4",
        "gpt-4o": "blackboxai/openai/gpt-4o",
        "claude-3.5-sonnet": "blackboxai/anthropic/claude-3.5-sonnet",
        "llama-3.1-70b": "blackboxai/meta-llama/llama-3.1-70b-instruct",
        "gemini-pro": "blackboxai/google/gemini-pro",
        "qwen-max": "blackboxai/qwen/qwen-max",
        "deepseek-coder": "blackboxai/deepseek/deepseek-coder"
    },
    "openai": {
        # Modelos OpenAI nativos
        "gpt-4": "gpt-4",
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-4-turbo-preview": "gpt-4-turbo-preview",
        "gpt-4-vision-preview": "gpt-4-vision-preview",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k": "gpt-3.5-turbo-16k"
    },
    "anthropic": {
        # Modelos Anthropic nativos
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3.5-haiku": "claude-3-5-haiku-20241022",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307"
    },
    "groq": {
        # Modelos Groq nativos
        "llama-3.1-70b": "llama-3.1-70b-versatile",
        "llama-3.1-8b": "llama-3.1-8b-instant",
        "llama-3.2-90b": "llama-3.2-90b-text-preview",
        "llama-3.2-11b": "llama-3.2-11b-text-preview",
        "llama-3.2-3b": "llama-3.2-3b-preview",
        "llama-3.2-1b": "llama-3.2-1b-preview",
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gemma-7b": "gemma-7b-it"
    },
    "together": {
        # Modelos Together AI nativos
        "llama-3.1-405b": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "llama-3.1-70b": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "llama-3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "qwen-2.5-72b": "Qwen/Qwen2.5-72B-Instruct-Turbo",
        "mixtral-8x22b": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "deepseek-coder": "deepseek-ai/deepseek-coder-33b-instruct"
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
    "blackbox": "gpt-4o",
    "chispart": "gpt-4o",
    "openai": "gpt-4o",
    "anthropic": "claude-3.5-sonnet",
    "groq": "llama-3.1-70b",
    "together": "llama-3.1-70b",
    "qwen": "qwen-max",
    "gemini": "gemini-1.5-pro",
    "codestral": "codestral-latest"
}

def get_api_config(api_name: str = None) -> Dict[str, Any]:
    """
    Obtiene configuración para una API específica
    
    Args:
        api_name: Nombre de la API
        
    Returns:
        Diccionario con configuración de la API
    """
    api_name = api_name or DEFAULT_API
    if api_name not in AVAILABLE_APIS:
        api_name = DEFAULT_API
    
    config = AVAILABLE_APIS[api_name]
    
    # Compatibilidad retro: permitir BLACKBOX_API_KEY o CHISPART_API_KEY
    if api_name in ['blackbox', 'chispart']:
        api_key = (os.getenv("CHISPART_API_KEY") or 
                  os.getenv("BLACKBOX_API_KEY") or 
                  config.get("default_key", ""))
    else:
        api_key = os.getenv(config["default_key_env"], config.get("default_key", ""))

    # Obtener timeouts optimizados
    timeouts = get_timeout_config()
    
    result = {
        "name": config["name"],
        "base_url": config["base_url"],
        "api_key": api_key,
        "supports_vision": config.get("supports_vision", False),
        "supports_pdf": config.get("supports_pdf", False),
        "timeout": timeouts["total_timeout"],
        "connect_timeout": timeouts["connect_timeout"],
        "read_timeout": timeouts["read_timeout"]
    }
    
    return result

def get_available_models(api_name: str = None) -> Dict[str, str]:
    """
    Obtiene modelos disponibles para una API
    
    Args:
        api_name: Nombre de la API
        
    Returns:
        Diccionario con modelos disponibles
    """
    api_name = api_name or DEFAULT_API
    return AVAILABLE_MODELS.get(api_name, AVAILABLE_MODELS[DEFAULT_API])

def get_default_model(api_name: str = None) -> str:
    """
    Obtiene modelo por defecto para una API
    
    Args:
        api_name: Nombre de la API
        
    Returns:
        Nombre del modelo por defecto
    """
    api_name = api_name or DEFAULT_API
    return DEFAULT_MODELS.get(api_name, DEFAULT_MODELS[DEFAULT_API])

def get_timeout_config() -> Dict[str, int]:
    """
    Obtiene configuración de timeouts optimizada
    
    Returns:
        Diccionario con timeouts
    """
    try:
        from termux_utils import get_mobile_optimized_timeouts, is_termux
        if is_termux():
            return get_mobile_optimized_timeouts()
    except ImportError:
        pass
    
    # Configuración por defecto
    return {
        'connect_timeout': 10,
        'read_timeout': 60,
        'total_timeout': 120
    }

def get_vision_supported_apis() -> List[str]:
    """
    Obtiene lista de APIs que soportan análisis de imágenes
    
    Returns:
        Lista de nombres de APIs
    """
    return [api_name for api_name, config in AVAILABLE_APIS.items() 
            if config.get("supports_vision", False)]

def get_pdf_supported_apis() -> List[str]:
    """
    Obtiene lista de APIs que soportan análisis de PDFs
    
    Returns:
        Lista de nombres de APIs
    """
    return [api_name for api_name, config in AVAILABLE_APIS.items() 
            if config.get("supports_pdf", False)]

def get_model_categories() -> Dict[str, List[str]]:
    """
    Categoriza modelos por tipo
    
    Returns:
        Diccionario con categorías de modelos
    """
    categories = {
        "OpenAI": [],
        "Anthropic": [],
        "Meta": [],
        "Google": [],
        "Mistral": [],
        "DeepSeek": [],
        "Qwen": [],
        "Código": [],
        "Matemáticas": [],
        "Otros": []
    }
    
    # Categorizar modelos de blackbox (más completo)
    blackbox_models = AVAILABLE_MODELS.get("blackbox", {})
    
    for model_name in blackbox_models.keys():
        model_lower = model_name.lower()
        
        if "gpt" in model_lower:
            categories["OpenAI"].append(model_name)
        elif "claude" in model_lower:
            categories["Anthropic"].append(model_name)
        elif "llama" in model_lower:
            categories["Meta"].append(model_name)
        elif "gemini" in model_lower:
            categories["Google"].append(model_name)
        elif any(x in model_lower for x in ["mixtral", "mistral", "mathstral"]):
            categories["Mistral"].append(model_name)
        elif "deepseek" in model_lower:
            categories["DeepSeek"].append(model_name)
        elif "qwen" in model_lower:
            categories["Qwen"].append(model_name)
        elif any(x in model_lower for x in ["code", "starcoder", "wizard"]):
            categories["Código"].append(model_name)
        elif "math" in model_lower:
            categories["Matemáticas"].append(model_name)
        else:
            categories["Otros"].append(model_name)
    
    # Remover categorías vacías
    return {k: v for k, v in categories.items() if v}

def validate_api_model_combination(api_name: str, model_name: str) -> bool:
    """
    Valida si una combinación de API y modelo es válida
    
    Args:
        api_name: Nombre de la API
        model_name: Nombre del modelo
        
    Returns:
        True si la combinación es válida
    """
    if api_name not in AVAILABLE_APIS:
        return False
    
    available_models = get_available_models(api_name)
    return model_name in available_models

def get_api_statistics() -> Dict[str, Any]:
    """
    Obtiene estadísticas de las APIs configuradas
    
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        "total_apis": len(AVAILABLE_APIS),
        "vision_apis": len(get_vision_supported_apis()),
        "pdf_apis": len(get_pdf_supported_apis()),
        "total_models": sum(len(models) for models in AVAILABLE_MODELS.values()),
        "models_by_api": {api: len(models) for api, models in AVAILABLE_MODELS.items()},
        "categories": {cat: len(models) for cat, models in get_model_categories().items()}
    }
    
    return stats

# Configuración específica para móviles
MOBILE_CONFIG = {
    "max_image_size_mb": 10,
    "max_pdf_size_mb": 15,
    "max_text_chars": 50000,
    "console_width": 70,
    "enable_rich_formatting": True,
    "use_compact_tables": True,
    "retry_attempts": 3,
    "retry_delay": 2,
    "chunk_size": 1024,
    "stream_timeout": 120
}

# Configuración de seguridad
SECURITY_CONFIG = {
    "whitelist_enabled": True,
    "allowed_commands": [
        "ls", "pwd", "cd", "cat", "grep", "find", "which", "echo", "date", "whoami",
        "git", "npm", "pip", "python", "python3", "node", "yarn",
        "mkdir", "touch", "cp", "mv", "chmod",
        "curl", "wget", "ping",
        "vim", "nano", "less", "more", "head", "tail"
    ],
    "blocked_commands": [
        "sudo", "su", "passwd", "useradd", "userdel", "usermod",
        "systemctl", "service", "mount", "umount", "fdisk", "mkfs",
        "iptables", "ufw", "firewall-cmd", "setenforce",
        "crontab", "at", "batch", "nc", "netcat", "nmap"
    ],
    "require_confirmation": [
        "rm", "rmdir", "mv", "cp", "chmod", "chown", "git push"
    ]
}

# Tipos de archivo soportados
SUPPORTED_FILE_TYPES = {
    "images": ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'],
    "documents": ['.pdf', '.txt', '.md', '.doc', '.docx'],
    "code": ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml'],
    "archives": ['.zip', '.tar', '.gz', '.rar', '.7z']
}
