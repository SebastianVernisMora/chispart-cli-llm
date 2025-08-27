import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
import base64

try:
    from core.api_key_manager import APIKeyManager
    API_KEY_MANAGER_AVAILABLE = True
except ImportError:
    API_KEY_MANAGER_AVAILABLE = False

class TestSecurity:
    def test_api_key_encryption(self, mock_config_dir):
        """Test encriptación de API keys"""
        if not API_KEY_MANAGER_AVAILABLE:
            pytest.skip("APIKeyManager not available")
        
        # Crear manager con ruta de almacenamiento en directorio temporal
        storage_path = os.path.join(mock_config_dir, 'api_keys.enc')
        manager = APIKeyManager(storage_path=storage_path)
        
        # Establecer API key
        test_key = "sk-test-api-key-12345-secret"
        manager.set_api_key('test_provider', test_key)
        
        # Verificar que el archivo existe
        assert os.path.exists(storage_path)
        
        # Leer el archivo y verificar que la clave no está en texto plano
        with open(storage_path, 'rb') as f:
            file_content = f.read().decode('utf-8', errors='ignore')
            assert test_key not in file_content
        
        # Verificar que podemos recuperar la clave correctamente
        retrieved_key = manager.get_api_key('test_provider')
        assert retrieved_key == test_key
    
    def test_api_key_permissions(self, mock_config_dir):
        """Test permisos de archivo de API keys"""
        if not API_KEY_MANAGER_AVAILABLE:
            pytest.skip("APIKeyManager not available")
        
        # Crear manager con ruta de almacenamiento en directorio temporal
        storage_path = os.path.join(mock_config_dir, 'api_keys.enc')
        manager = APIKeyManager(storage_path=storage_path)
        
        # Establecer API key para crear el archivo
        manager.set_api_key('test_provider', 'test_key')
        
        # Verificar permisos (solo en sistemas Unix)
        if os.name == 'posix':
            permissions = oct(os.stat(storage_path).st_mode & 0o777)
            assert permissions.endswith('600')
    
    def test_sql_injection_protection(self, app_client):
        """Test protección contra SQL injection"""
        # Lista de payloads maliciosos
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in sql_payloads:
            # Probar en endpoint de chat
            response = app_client.post('/api/chat',
                                     json={'message': payload, 'api': 'test'},
                                     content_type='application/json')
            
            # No debería causar un error 500 (error interno del servidor)
            assert response.status_code != 500
    
    def test_xss_protection(self, app_client):
        """Test protección contra XSS"""
        # Lista de payloads XSS
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            # Probar en endpoint de chat
            response = app_client.post('/api/chat',
                                     json={'message': payload, 'api': 'test'},
                                     content_type='application/json')
            
            # No debería causar un error 500
            assert response.status_code != 500
            
            # Si la respuesta es 200, verificar que el payload no se refleja sin escapar
            if response.status_code == 200:
                data = json.loads(response.data)
                if 'response' in data:
                    assert payload not in data['response']
    
    def test_file_upload_security(self, app_client):
        """Test seguridad en upload de archivos"""
        # Crear archivo temporal malicioso
        with tempfile.NamedTemporaryFile(suffix='.php') as temp_file:
            temp_file.write(b"<?php system($_GET['cmd']); ?>")
            temp_file.flush()
            
            # Intentar subir archivo PHP usando content_type correcto
            with open(temp_file.name, 'rb') as f:
                response = app_client.post('/api/image',
                                         data={'api': 'test', 'prompt': 'test', 'image': (f, os.path.basename(temp_file.name))},
                                         content_type='multipart/form-data')
            
            # Debería ser rechazado
            assert response.status_code in [400, 415, 422]
    
    def test_csrf_protection(self, app_client):
        """Test protección CSRF"""
        # Las peticiones POST sin token CSRF deberían ser rechazadas
        # si la aplicación tiene protección CSRF habilitada
        
        # Este test es más un recordatorio de que se debe implementar protección CSRF
        # La implementación real dependerá de cómo se configure Flask-WTF o similar
        
        # Por ahora, verificamos que las peticiones POST funcionan con el content-type correcto
        response = app_client.post('/api/config',
                                 json={'config': {'theme': 'dark'}},
                                 content_type='application/json')
        
        assert response.status_code in [200, 400, 401, 403]
