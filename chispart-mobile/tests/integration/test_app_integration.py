import pytest
import json
from unittest.mock import patch, MagicMock

class TestAppIntegration:
    @patch('app.is_termux')
    def test_app_initialization(self, mock_is_termux, app_client):
        """Test inicialización de la aplicación"""
        mock_is_termux.return_value = False
        
        # Verificar que la app está en modo testing
        assert app_client.application.config['TESTING'] == True
    
    @patch('app.is_termux')
    def test_index_route(self, mock_is_termux, app_client):
        """Test ruta principal"""
        mock_is_termux.return_value = False
        
        response = app_client.get('/')
        assert response.status_code == 200
        assert b'Chispart' in response.data
    
    @patch('app.is_termux')
    def test_chat_route(self, mock_is_termux, app_client):
        """Test ruta de chat"""
        mock_is_termux.return_value = False
        
        response = app_client.get('/chat')
        assert response.status_code == 200
    
    @patch('app.is_termux')
    def test_config_route(self, mock_is_termux, app_client):
        """Test ruta de configuración"""
        mock_is_termux.return_value = False
        
        response = app_client.get('/config')
        assert response.status_code == 200
    
    @patch('app.is_termux')
    def test_api_stats_endpoint(self, mock_is_termux, app_client):
        """Test endpoint de estadísticas"""
        mock_is_termux.return_value = False
        
        response = app_client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'app' in data
        assert 'version' in data['app']
    
    @patch('app.is_termux')
    def test_api_config_endpoint(self, mock_is_termux, app_client):
        """Test endpoint de configuración"""
        mock_is_termux.return_value = False
        
        response = app_client.get('/api/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'config' in data
        assert 'api_providers' in data
    
    @patch('app.is_termux')
    def test_chat_endpoint_validation(self, mock_is_termux, app_client):
        """Test validación de endpoint de chat"""
        mock_is_termux.return_value = False
        
        # Mensaje vacío debe ser rechazado
        response = app_client.post('/api/chat', 
                                 json={'message': ''},
                                 content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
