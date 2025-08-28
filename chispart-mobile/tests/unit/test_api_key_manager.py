import pytest
import os
import tempfile
from unittest.mock import patch, mock_open

try:
    from core.api_key_manager import APIKeyManager

    API_KEY_MANAGER_AVAILABLE = True
except ImportError:
    API_KEY_MANAGER_AVAILABLE = False


@pytest.mark.skipif(not API_KEY_MANAGER_AVAILABLE, reason="APIKeyManager not available")
class TestAPIKeyManager:
    def test_init(self, mock_config_dir):
        """Test inicialización del manager"""
        # Crear archivo de storage en lugar de directorio
        storage_file = os.path.join(mock_config_dir, "api_keys.json")
        manager = APIKeyManager(storage_path=storage_file)
        assert manager.storage_path == storage_file
        # Verificar que el manager se inicializa correctamente
        assert hasattr(manager, "storage_path")

    def test_set_and_get_api_key(self, mock_config_dir):
        """Test set y get de API key"""
        # Crear archivo de storage en lugar de directorio
        storage_file = os.path.join(mock_config_dir, "api_keys.json")
        manager = APIKeyManager(storage_path=storage_file)

        # Set API key
        result = manager.set_api_key("test_provider", "test_key_123")
        assert result == True

        # Get API key
        retrieved_key = manager.get_api_key("test_provider")
        assert retrieved_key == "test_key_123"

    def test_list_providers(self, mock_config_dir):
        """Test listar proveedores"""
        # Crear archivo de storage en lugar de directorio
        storage_file = os.path.join(mock_config_dir, "api_keys.json")
        manager = APIKeyManager(storage_path=storage_file)

        # Agregar algunos proveedores
        manager.set_api_key("provider1", "key1")
        manager.set_api_key("provider2", "key2")

        providers = manager.list_providers()
        provider_names = [p["provider"] for p in providers]

        assert "provider1" in provider_names
        assert "provider2" in provider_names

    def test_remove_api_key(self, mock_config_dir):
        """Test remover API key"""
        # Crear archivo de storage en lugar de directorio
        storage_file = os.path.join(mock_config_dir, "api_keys.json")
        manager = APIKeyManager(storage_path=storage_file)

        # Agregar y luego remover
        manager.set_api_key("test_provider", "test_key")
        assert manager.get_api_key("test_provider") == "test_key"

        result = manager.remove_api_key("test_provider")
        assert result == True
        assert manager.get_api_key("test_provider") is None
