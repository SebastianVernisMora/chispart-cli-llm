"""
Datos de prueba para los tests de Chispart Mobile
"""

# Datos de prueba para API Keys
API_KEYS_TEST_DATA = {
    "blackbox": "sk-test-blackbox-key-12345",
    "openai": "sk-test-openai-key-67890",
    "anthropic": "sk-test-anthropic-key-abcde",
    "groq": "sk-test-groq-key-fghij",
    "together": "sk-test-together-key-klmno",
}

# Datos de prueba para configuración
CONFIG_TEST_DATA = {
    "theme": "dark",
    "language": "es",
    "default_api": "blackbox",
    "default_model": "gpt-4",
    "show_token_usage": True,
    "compact_mode": False,
    "animations_enabled": True,
    "offline_mode": True,
    "notifications_enabled": True,
}

# Datos de prueba para mensajes de chat
CHAT_MESSAGES_TEST_DATA = [
    {"message": "Hola, ¿cómo estás?", "api": "blackbox", "model": "gpt-4"},
    {
        "message": "¿Cuál es la capital de Francia?",
        "api": "openai",
        "model": "gpt-3.5-turbo",
    },
    {
        "message": "Explica la teoría de la relatividad",
        "api": "anthropic",
        "model": "claude-3-haiku",
    },
]

# Datos de prueba para respuestas de chat
CHAT_RESPONSES_TEST_DATA = [
    {
        "response": "Hola, estoy bien. ¿En qué puedo ayudarte hoy?",
        "model_used": "gpt-4",
        "api_used": "blackbox",
        "usage": {"prompt_tokens": 10, "completion_tokens": 12, "total_tokens": 22},
    },
    {
        "response": "La capital de Francia es París.",
        "model_used": "gpt-3.5-turbo",
        "api_used": "openai",
        "usage": {"prompt_tokens": 8, "completion_tokens": 7, "total_tokens": 15},
    },
    {
        "response": "La teoría de la relatividad, propuesta por Albert Einstein, se divide en dos partes principales: la teoría de la relatividad especial (1905) y la teoría de la relatividad general (1915)...",
        "model_used": "claude-3-haiku",
        "api_used": "anthropic",
        "usage": {"prompt_tokens": 9, "completion_tokens": 35, "total_tokens": 44},
    },
]

# Datos de prueba para PWA
PWA_CONFIG_TEST_DATA = {
    "app_name": "Chispart Mobile Test",
    "short_name": "Chispart Test",
    "description": "Test PWA for Chispart Mobile",
    "theme_color": "#00FF88",
    "background_color": "#1A1A1A",
    "display": "standalone",
    "orientation": "portrait-primary",
    "start_url": "/",
    "scope": "/",
    "cache_strategy": "cache_first",
}

# Datos de prueba para errores
ERROR_MESSAGES_TEST_DATA = {
    "api_key_missing": "API key no configurada",
    "api_key_invalid": "API key inválida",
    "network_error": "Error de red",
    "server_error": "Error del servidor",
    "validation_error": "Error de validación",
}

# Datos de prueba para archivos
TEST_FILES = {
    "valid_image": {
        "name": "test_image.jpg",
        "content": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff",  # Cabecera JPEG mínima
        "mime": "image/jpeg",
    },
    "valid_png": {
        "name": "test_image.png",
        "content": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n\x13\xe9\x00\x00\x00\x00IEND\xaeB`\x82",  # PNG mínimo
        "mime": "image/png",
    },
    "invalid_php": {
        "name": "malicious.php",
        "content": b'<?php system($_GET["cmd"]); ?>',
        "mime": "application/octet-stream",
    },
    "invalid_exe": {
        "name": "malicious.exe",
        "content": b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00",  # Cabecera EXE mínima
        "mime": "application/octet-stream",
    },
}

# Datos de prueba para estadísticas
STATS_TEST_DATA = {
    "app": {"version": "1.0.0", "is_mobile": False, "platform": "Desktop"},
    "api_keys": {
        "total_keys": 3,
        "valid_keys": 2,
        "invalid_keys": 1,
        "total_usage": 42,
        "providers": ["blackbox", "openai", "anthropic"],
    },
    "config": {
        "total_schemas": 25,
        "configured_values": 15,
        "default_values": 10,
        "sensitive_values": 5,
    },
    "pwa": {
        "version": "test-version-123",
        "max_size": 50 * 1024 * 1024,
        "estimated_size": 2 * 1024 * 1024,
        "last_updated": "2025-01-01T12:00:00Z",
    },
}
