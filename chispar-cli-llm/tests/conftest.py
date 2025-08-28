"""
Configuración global de pytest para Chispart CLI
Fixtures compartidas y configuración de testing
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch
from pathlib import Path

# Importar módulos del proyecto
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config_extended import AVAILABLE_APIS, DEFAULT_API
from api_client import UniversalAPIClient


@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_env_vars():
    """Mock de variables de entorno para testing"""
    with patch.dict(os.environ, {
        'BLACKBOX_API_KEY': 'test_blackbox_key',
        'CHISPART_API_KEY': 'test_chispart_key',
        'QWEN_API_KEY': 'test_qwen_key',
        'GEMINI_API_KEY': 'test_gemini_key',
        'CODESTRAL_API_KEY': 'test_codestral_key'
    }):
        yield


@pytest.fixture
def mock_api_client():
    """Mock del cliente API universal"""
    client = MagicMock(spec=UniversalAPIClient)
    
    # Mock de respuesta exitosa
    mock_response = {
        "choices": [{
            "message": {
                "content": "Test response from AI"
            }
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
    
    client.chat_completions.return_value = mock_response
    client.extract_response_content.return_value = "Test response from AI"
    client.get_usage_info.return_value = {"total_tokens": 30}
    
    return client


@pytest.fixture
def sample_chat_history():
    """Historial de chat de ejemplo para tests"""
    return [
        {
            "type": "chat",
            "api": "chispart",
            "model": "gpt-4",
            "message": "Hola",
            "response": "¡Hola! ¿Cómo puedo ayudarte?",
            "usage": {"total_tokens": 15},
            "timestamp": "2025-01-01T12:00:00"
        },
        {
            "type": "chat",
            "api": "chispart", 
            "model": "claude-3.5-sonnet",
            "message": "¿Qué es Python?",
            "response": "Python es un lenguaje de programación...",
            "usage": {"total_tokens": 45},
            "timestamp": "2025-01-01T12:05:00"
        }
    ]


@pytest.fixture
def sample_team_data():
    """Datos de equipo de ejemplo para tests"""
    return {
        "name": "Equipo Test",
        "description": "Equipo de desarrollo para testing",
        "project_type": "web",
        "tech_stack": ["Python", "JavaScript", "Docker"],
        "preferred_apis": ["chispart", "qwen"],
        "members": [
            {
                "name": "Developer 1",
                "profile": "backend",
                "role": "senior",
                "specialties": ["APIs", "databases"],
                "preferred_models": ["gpt-4", "claude-3.5-sonnet"]
            }
        ]
    }


@pytest.fixture
def mock_subprocess():
    """Mock de subprocess para tests de ejecución de comandos"""
    with patch('subprocess.run') as mock_run:
        # Configurar respuesta exitosa por defecto
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Command executed successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_console():
    """Mock de Rich Console para tests de UI"""
    with patch('rich.console.Console') as mock_console_class:
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        yield mock_console


@pytest.fixture
def sample_image_file(temp_dir):
    """Crea un archivo de imagen de ejemplo para tests"""
    image_path = os.path.join(temp_dir, "test_image.jpg")
    # Crear un archivo de imagen falso
    with open(image_path, 'wb') as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # Header JPEG básico
    return image_path


@pytest.fixture
def sample_pdf_file(temp_dir):
    """Crea un archivo PDF de ejemplo para tests"""
    pdf_path = os.path.join(temp_dir, "test_document.pdf")
    # Crear un archivo PDF falso con header básico
    with open(pdf_path, 'wb') as f:
        f.write(b'%PDF-1.4\n%Test PDF content')
    return pdf_path


@pytest.fixture
def mock_click_context():
    """Mock de contexto de Click para tests de CLI"""
    from click.testing import CliRunner
    runner = CliRunner()
    
    # Mock del contexto
    ctx = MagicMock()
    ctx.obj = {'api': DEFAULT_API}
    
    return ctx, runner


@pytest.fixture(autouse=True)
def reset_managers():
    """Reset de managers globales antes de cada test"""
    # Importar managers
    try:
        from core.dev_profiles import profile_manager
        from core.team_manager import team_manager
        from core.security_manager import security_manager
        
        # Reset estado si es necesario
        # Esto evita interferencia entre tests
        pass
    except ImportError:
        # Los managers pueden no estar disponibles en todos los tests
        pass


@pytest.fixture
def mock_file_operations():
    """Mock de operaciones de archivo para tests"""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_exists.return_value = True
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'makedirs': mock_makedirs
        }


# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest"""
    # Agregar marcadores personalizados
    config.addinivalue_line(
        "markers", "slow: marca tests que son lentos de ejecutar"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios"
    )
    config.addinivalue_line(
        "markers", "cli: marca tests específicos de CLI"
    )
    config.addinivalue_line(
        "markers", "security: marca tests de seguridad"
    )


# Configuración de logging para tests
import logging
logging.getLogger().setLevel(logging.WARNING)
