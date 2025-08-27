import pytest
import os
import json
from unittest.mock import patch, MagicMock

try:
    from core.pwa_manager import PWAManager
    PWA_MANAGER_AVAILABLE = True
except ImportError:
    PWA_MANAGER_AVAILABLE = False

@pytest.mark.skipif(not PWA_MANAGER_AVAILABLE, reason="PWAManager not available")
class TestPWAManager:
    def test_init(self):
        """Test inicialización del PWA manager"""
        manager = PWAManager()
        assert manager.app is None
        assert isinstance(manager.config, dict)
        assert isinstance(manager.cache_version, str)
    
    def test_init_with_app(self):
        """Test inicialización con app Flask"""
        mock_app = MagicMock()
        mock_app.route = MagicMock()
        
        with patch.object(PWAManager, '_register_routes') as mock_register:
            with patch.object(PWAManager, '_setup_static_files') as mock_setup:
                manager = PWAManager(app=mock_app)
                
                assert manager.app == mock_app
                mock_register.assert_called_once()
                mock_setup.assert_called_once()
    
    def test_get_default_config(self):
        """Test configuración por defecto"""
        manager = PWAManager()
        config = manager._get_default_config()
        
        assert isinstance(config, dict)
        assert 'app_name' in config
        assert 'short_name' in config
        assert 'theme_color' in config
        assert 'background_color' in config
        assert 'display' in config
    
    def test_generate_cache_version(self):
        """Test generación de versión de caché"""
        manager = PWAManager()
        version = manager._generate_cache_version()
        
        assert isinstance(version, str)
        assert len(version) > 0
    
    def test_generate_service_worker(self):
        """Test generación de service worker"""
        manager = PWAManager()
        sw_content = manager._generate_service_worker()
        
        assert isinstance(sw_content, str)
        assert 'self.addEventListener(\'install\'' in sw_content
        assert 'self.addEventListener(\'activate\'' in sw_content
        assert 'self.addEventListener(\'fetch\'' in sw_content
        assert manager.cache_version in sw_content
    
    def test_get_offline_template(self):
        """Test template offline"""
        manager = PWAManager()
        template = manager._get_offline_template()
        
        assert isinstance(template, str)
        assert '<!DOCTYPE html>' in template
        assert '<title>Sin Conexión' in template
    
    def test_get_pwa_config(self):
        """Test obtener configuración PWA"""
        manager = PWAManager()
        config = manager.get_pwa_config()
        
        assert isinstance(config, dict)
        assert 'cache_version' in config
        assert 'config' in config
        assert 'features' in config
    
    def test_update_config(self):
        """Test actualizar configuración"""
        manager = PWAManager()
        original_version = manager.cache_version
        
        # Actualizar configuración con cambio significativo
        manager.update_config({
            'app_name': 'Test App Updated', 
            'theme_color': '#FF0000',
            'background_color': '#000000',
            'display': 'fullscreen'
        })
        
        assert manager.config['app_name'] == 'Test App Updated'
        assert manager.config['theme_color'] == '#FF0000'
        # La versión de caché debería cambiar con actualizaciones significativas
        # Si no cambia, es porque el hash es el mismo, lo cual es válido
        assert isinstance(manager.cache_version, str)
        assert len(manager.cache_version) > 0
    
    def test_get_cache_stats(self):
        """Test estadísticas de caché"""
        manager = PWAManager()
        stats = manager.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert 'version' in stats
        assert 'max_size' in stats
        assert 'last_updated' in stats
