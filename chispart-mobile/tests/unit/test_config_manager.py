import pytest
import os

try:
    from core.config_manager import ConfigManager, ConfigLevel, ConfigScope

    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False


@pytest.mark.skipif(not CONFIG_MANAGER_AVAILABLE, reason="ConfigManager not available")
class TestConfigManager:
    def test_init(self, mock_config_dir):
        """Test inicialización del config manager"""
        manager = ConfigManager(config_dir=mock_config_dir)
        assert manager.config_dir == mock_config_dir

    def test_set_and_get_config(self, mock_config_dir):
        """Test set y get de configuración"""
        manager = ConfigManager(config_dir=mock_config_dir)

        # Set config
        result = manager.set("test_key", "test_value")
        assert result == True

        # Get config
        value = manager.get("test_key")
        assert value == "test_value"

    def test_default_values(self, mock_config_dir):
        """Test valores por defecto"""
        manager = ConfigManager(config_dir=mock_config_dir)

        # Obtener valor que no existe debería retornar default
        value = manager.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_config_persistence(self, mock_config_dir):
        """Test persistencia de configuración"""
        # Crear primer manager y set value
        manager1 = ConfigManager(config_dir=mock_config_dir)
        manager1.set("persistent_key", "persistent_value")

        # Crear segundo manager y verificar que persiste
        manager2 = ConfigManager(config_dir=mock_config_dir)
        value = manager2.get("persistent_key")
        assert value == "persistent_value"
