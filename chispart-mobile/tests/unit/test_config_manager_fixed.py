import pytest
import os

try:
    from core.config_manager import AdvancedConfigManager, ConfigLevel, ConfigScope
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False

@pytest.mark.skipif(not CONFIG_MANAGER_AVAILABLE, reason="AdvancedConfigManager not available")
class TestAdvancedConfigManager:
    def test_init(self, mock_config_dir):
        """Test inicialización del config manager"""
        manager = AdvancedConfigManager(config_dir=mock_config_dir)
        assert manager.config_dir == mock_config_dir
    
    def test_set_and_get_config(self, mock_config_dir):
        """Test set y get de configuración"""
        manager = AdvancedConfigManager(config_dir=mock_config_dir)
        
        # Set config
        result = manager.set('test_key', 'test_value')
        assert result == True
        
        # Get config
        value = manager.get('test_key')
        assert value == 'test_value'
    
    def test_default_values(self, mock_config_dir):
        """Test valores por defecto"""
        manager = AdvancedConfigManager(config_dir=mock_config_dir)
        
        # Obtener valor que no existe debería retornar default
        value = manager.get('nonexistent_key', 'default_value')
        assert value == 'default_value'
    
    def test_config_levels(self, mock_config_dir):
        """Test niveles de configuración"""
        manager = AdvancedConfigManager(config_dir=mock_config_dir)
        
        # Establecer valores en diferentes niveles
        manager.set('level_key', 'system_value', level=ConfigLevel.SYSTEM)
        manager.set('level_key', 'user_value', level=ConfigLevel.USER)
        manager.set('level_key', 'session_value', level=ConfigLevel.SESSION)
        
        # El valor de mayor prioridad debe ser retornado (SESSION > USER > SYSTEM)
        assert manager.get('level_key') == 'session_value'
        
        # Test simplificado: verificar que el sistema maneja múltiples niveles
        # La implementación actual usa un enfoque simplificado para testing
        assert manager.get('level_key') in ['session_value', 'user_value', 'system_value']
        assert isinstance(manager.get('level_key'), str)
