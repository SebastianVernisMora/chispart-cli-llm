import pytest
import json
import os
from unittest.mock import patch, MagicMock

class TestPWAFunctionality:
    def test_manifest_endpoint(self, app_client):
        """Test endpoint de manifest.json"""
        response = app_client.get('/manifest.json')
        assert response.status_code == 200
        # PWA manifest usa application/manifest+json
        assert 'application/manifest+json' in response.content_type or 'application/json' in response.content_type
        
        data = json.loads(response.data)
        assert 'name' in data
        assert 'short_name' in data
        assert 'icons' in data
        assert 'start_url' in data
        assert 'display' in data
        assert 'theme_color' in data
        assert 'background_color' in data
    
    def test_service_worker_endpoint(self, app_client):
        """Test endpoint de service worker"""
        response = app_client.get('/sw.js')
        assert response.status_code == 200
        # Service worker puede incluir charset
        assert 'application/javascript' in response.content_type
        
        content = response.data.decode('utf-8')
        assert 'self.addEventListener(\'install\'' in content
        assert 'self.addEventListener(\'activate\'' in content
        assert 'self.addEventListener(\'fetch\'' in content
    
    def test_offline_page(self, app_client):
        """Test página offline"""
        response = app_client.get('/offline')
        assert response.status_code == 200
        assert b'Sin Conexi' in response.data  # "Sin Conexión" en español
    
    def test_cache_status_endpoint(self, app_client):
        """Test endpoint de estado de caché"""
        response = app_client.get('/api/pwa/cache-status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'cache_version' in data
        assert 'last_updated' in data
        assert 'config' in data
    
    def test_sync_endpoint(self, app_client):
        """Test endpoint de sincronización"""
        # Test de sincronización de chat
        response = app_client.post('/api/pwa/sync',
                                 json={'type': 'chat_history', 'payload': {'items': []}},
                                 content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'success' in data
        
        # Test de tipo desconocido
        response = app_client.post('/api/pwa/sync',
                                 json={'type': 'unknown', 'payload': {}},
                                 content_type='application/json')
        assert response.status_code == 400
    
    def test_static_files_existence(self):
        """Test existencia de archivos estáticos necesarios"""
        static_dir = os.path.join(os.getcwd(), 'static')
        
        # Verificar directorios
        assert os.path.exists(static_dir)
        assert os.path.exists(os.path.join(static_dir, 'js'))
        assert os.path.exists(os.path.join(static_dir, 'css'))
        
        # Verificar archivos críticos
        assert os.path.exists(os.path.join(static_dir, 'manifest.json'))
        assert os.path.exists(os.path.join(static_dir, 'sw.js'))
