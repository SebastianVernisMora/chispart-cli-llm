import pytest
import tempfile
import os
import sys
from unittest.mock import patch

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def temp_dir():
    """Fixture para crear directorio temporal"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_config_dir(temp_dir):
    """Fixture para mockear directorio de configuración"""
    config_dir = os.path.join(temp_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

@pytest.fixture
def app_client():
    """Fixture para cliente de testing de Flask"""
    try:
        from app import app_instance
        app_instance.app.config['TESTING'] = True
        app_instance.app.config['WTF_CSRF_ENABLED'] = False
        with app_instance.app.test_client() as client:
            yield client
    except ImportError:
        pytest.skip("Flask app not available")

@pytest.fixture
def mock_api_key():
    """Fixture para API key de testing"""
    return "test_api_key_12345"

@pytest.fixture(autouse=True)
def mock_environment():
    """Fixture para mockear variables de entorno"""
    with patch.dict(os.environ, {
        'FLASK_ENV': 'testing',
        'TESTING': 'true'
    }):
        yield
