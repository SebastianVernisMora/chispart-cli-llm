"""
Tests para config_extended.py
Incluye tests para configuración de APIs, modelos y optimizaciones
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config_extended import (
    get_api_config, get_available_models, get_default_model,
    AVAILABLE_APIS, DEFAULT_API, AVAILABLE_MODELS, DEFAULT_MODELS,
    VISION_SUPPORTED_APIS, PDF_SUPPORTED_APIS, get_security_config
)


class TestAPIConfiguration:
    """Tests para configuración de APIs"""
    
    @pytest.mark.unit
    def test_available_apis_structure(self):
        """Test estructura de APIs disponibles"""
        assert isinstance(AVAILABLE_APIS, dict)
        assert len(AVAILABLE_APIS) > 0
        
        # Verificar que cada API tiene la estructura correcta
        for api_name, api_config in AVAILABLE_APIS.items():
            assert 'name' in api_config
            assert 'base_url' in api_config
            assert 'default_key_env' in api_config
            assert isinstance(api_config['name'], str)
            assert isinstance(api_config['base_url'], str)
            assert isinstance(api_config['default_key_env'], str)
    
    @pytest.mark.unit
    def test_default_api_exists(self):
        """Test que la API por defecto existe"""
        assert DEFAULT_API in AVAILABLE_APIS
    
    @pytest.mark.unit
    def test_get_api_config_default(self):
        """Test obtener configuración de API por defecto"""
        with patch.dict(os.environ, {'BLACKBOX_API_KEY': 'test_key'}):
            config = get_api_config()
            
            assert config['name'] == AVAILABLE_APIS[DEFAULT_API]['name']
            assert config['base_url'] == AVAILABLE_APIS[DEFAULT_API]['base_url']
            assert config['api_key'] == 'test_key'
            assert 'timeout' in config
    
    @pytest.mark.unit
    def test_get_api_config_specific_api(self):
        """Test obtener configuración de API específica"""
        with patch.dict(os.environ, {'QWEN_API_KEY': 'qwen_test_key'}):
            config = get_api_config('qwen')
            
            assert config['name'] == AVAILABLE_APIS['qwen']['name']
            assert config['base_url'] == AVAILABLE_APIS['qwen']['base_url']
            assert config['api_key'] == 'qwen_test_key'
    
    @pytest.mark.unit
    def test_get_api_config_chispart_compatibility(self):
        """Test compatibilidad de claves API para Chispart"""
        # Test con CHISPART_API_KEY
        with patch.dict(os.environ, {'CHISPART_API_KEY': 'chispart_key'}):
            config = get_api_config('chispart')
            assert config['api_key'] == 'chispart_key'
        
        # Test con BLACKBOX_API_KEY (compatibilidad)
        with patch.dict(os.environ, {'BLACKBOX_API_KEY': 'blackbox_key'}):
            config = get_api_config('chispart')
            assert config['api_key'] == 'blackbox_key'
        
        # Test prioridad CHISPART_API_KEY sobre BLACKBOX_API_KEY
        with patch.dict(os.environ, {
            'CHISPART_API_KEY': 'chispart_key',
            'BLACKBOX_API_KEY': 'blackbox_key'
        }):
            config = get_api_config('chispart')
            assert config['api_key'] == 'chispart_key'
    
    @pytest.mark.unit
    def test_get_api_config_invalid_api(self):
        """Test configuración con API inválida usa por defecto"""
        with patch.dict(os.environ, {'BLACKBOX_API_KEY': 'test_key'}):
            config = get_api_config('invalid_api')
            
            # Debe usar la API por defecto
            assert config['name'] == AVAILABLE_APIS[DEFAULT_API]['name']


class TestModelsConfiguration:
    """Tests para configuración de modelos"""
    
    @pytest.mark.unit
    def test_available_models_structure(self):
        """Test estructura de modelos disponibles"""
        assert isinstance(AVAILABLE_MODELS, dict)
        
        # Verificar que cada API tiene modelos
        for api_name in AVAILABLE_APIS.keys():
            assert api_name in AVAILABLE_MODELS
            assert isinstance(AVAILABLE_MODELS[api_name], dict)
            assert len(AVAILABLE_MODELS[api_name]) > 0
    
    @pytest.mark.unit
    def test_default_models_exist(self):
        """Test que los modelos por defecto existen"""
        for api_name, default_model in DEFAULT_MODELS.items():
            assert api_name in AVAILABLE_MODELS
            assert default_model in AVAILABLE_MODELS[api_name]
    
    @pytest.mark.unit
    def test_get_available_models_default(self):
        """Test obtener modelos disponibles por defecto"""
        models = get_available_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        assert models == AVAILABLE_MODELS[DEFAULT_API]
    
    @pytest.mark.unit
    def test_get_available_models_specific_api(self):
        """Test obtener modelos de API específica"""
        for api_name in AVAILABLE_APIS.keys():
            models = get_available_models(api_name)
            
            assert isinstance(models, dict)
            assert len(models) > 0
            assert models == AVAILABLE_MODELS[api_name]
    
    @pytest.mark.unit
    def test_get_default_model(self):
        """Test obtener modelo por defecto"""
        # Test modelo por defecto general
        default_model = get_default_model()
        assert default_model == DEFAULT_MODELS[DEFAULT_API]
        
        # Test modelo por defecto de API específica
        for api_name in AVAILABLE_APIS.keys():
            default_model = get_default_model(api_name)
            assert default_model == DEFAULT_MODELS[api_name]
    
    @pytest.mark.unit
    def test_chispart_models_comprehensive(self):
        """Test que Chispart tiene modelos comprehensivos"""
        chispart_models = AVAILABLE_MODELS['chispart']
        
        # Verificar categorías de modelos
        model_categories = {
            'gpt': ['gpt-4', 'gpt-4o', 'gpt-3.5-turbo'],
            'claude': ['claude-3.5-sonnet', 'claude-3-opus'],
            'llama': ['llama-3.1-405b', 'llama-3.1-70b'],
            'gemini': ['gemini-2.5-flash', 'gemini-pro'],
            'qwen': ['qwen-max', 'qwen-2.5-72b'],
            'deepseek': ['deepseek-r1', 'deepseek-chat'],
            'codellama': ['codellama-70b', 'codellama-34b']
        }
        
        for category, expected_models in model_categories.items():
            category_models = [name for name in chispart_models.keys() 
                             if category in name.lower()]
            assert len(category_models) > 0, f"No se encontraron modelos de {category}"


class TestSupportedFeatures:
    """Tests para características soportadas"""
    
    @pytest.mark.unit
    def test_vision_supported_apis(self):
        """Test APIs que soportan visión"""
        assert isinstance(VISION_SUPPORTED_APIS, list)
        assert len(VISION_SUPPORTED_APIS) > 0
        
        # Verificar que las APIs existen
        for api_name in VISION_SUPPORTED_APIS:
            assert api_name in AVAILABLE_APIS
    
    @pytest.mark.unit
    def test_pdf_supported_apis(self):
        """Test APIs que soportan PDF"""
        assert isinstance(PDF_SUPPORTED_APIS, list)
        assert len(PDF_SUPPORTED_APIS) > 0
        
        # Verificar que las APIs existen
        for api_name in PDF_SUPPORTED_APIS:
            assert api_name in AVAILABLE_APIS


class TestSecurityConfiguration:
    """Tests para configuración de seguridad"""
    
    @pytest.fixture
    def security_config(self):
        """Fixture para obtener la configuración de seguridad del plan 'pro' para testing."""
        return get_security_config('pro')

    @pytest.mark.unit
    def test_security_config_structure(self, security_config):
        """Test estructura de configuración de seguridad"""
        assert isinstance(security_config, dict)
        
        required_keys = [
            'whitelist_enabled', 'allowed_commands', 
            'blocked_commands', 'require_confirmation'
        ]
        
        for key in required_keys:
            assert key in security_config
    
    @pytest.mark.unit
    def test_allowed_commands_comprehensive(self, security_config):
        """Test que los comandos permitidos son comprehensivos"""
        allowed_commands = security_config['allowed_commands']
        
        assert isinstance(allowed_commands, list)
        assert len(allowed_commands) > 0
        
        # Verificar categorías de comandos
        command_categories = {
            'basic': ['ls', 'pwd', 'cd', 'cat'],
            'development': ['git', 'npm', 'pip', 'python'],
            'files': ['mkdir', 'touch', 'cp', 'mv'],
            'text': ['vim', 'nano', 'grep', 'sort']
        }
        
        for category, expected_commands in command_categories.items():
            for cmd in expected_commands:
                assert cmd in allowed_commands, f"Comando {cmd} no está en permitidos"
    
    @pytest.mark.unit
    def test_blocked_commands_security(self, security_config):
        """Test que los comandos bloqueados son de seguridad"""
        blocked_commands = security_config['blocked_commands']
        
        assert isinstance(blocked_commands, list)
        assert len(blocked_commands) > 0
        
        # Verificar comandos peligrosos específicos
        dangerous_commands = ['sudo', 'su', 'rm -rf', 'passwd', 'systemctl']
        
        for cmd in dangerous_commands:
            # Verificar que el comando o parte de él está bloqueado
            is_blocked = any(cmd in blocked_cmd for blocked_cmd in blocked_commands)
            assert is_blocked, f"Comando peligroso {cmd} no está bloqueado"
    
    @pytest.mark.unit
    def test_require_confirmation_commands(self, security_config):
        """Test comandos que requieren confirmación"""
        confirmation_commands = security_config['require_confirmation']
        
        assert isinstance(confirmation_commands, list)
        assert len(confirmation_commands) > 0
        
        # Verificar comandos que deberían requerir confirmación
        should_confirm = ['rm', 'mv', 'chmod', 'git push']
        
        for cmd in should_confirm:
            is_in_confirmation = any(cmd in conf_cmd for conf_cmd in confirmation_commands)
            assert is_in_confirmation, f"Comando {cmd} debería requerir confirmación"


class TestTermuxOptimizations:
    """Tests para optimizaciones de Termux"""
    
    @pytest.mark.unit
    @patch('config_extended.is_termux')
    @patch('config_extended.get_mobile_optimized_timeouts')
    def test_termux_timeout_optimization(self, mock_get_timeouts, mock_is_termux):
        """Test optimización de timeouts para Termux"""
        # Simular entorno Termux
        mock_is_termux.return_value = True
        mock_get_timeouts.return_value = {
            'total_timeout': 120,
            'connect_timeout': 10,
            'read_timeout': 120
        }
        
        # Usar la función _get_timeouts directamente
        from config_extended import _get_timeouts
        timeouts = _get_timeouts()
        
        # Verificar que se aplicaron los timeouts optimizados
        assert timeouts['REQUEST_TIMEOUT'] == 120
        assert timeouts['CONNECT_TIMEOUT'] == 10
        assert timeouts['READ_TIMEOUT'] == 120
    
    @pytest.mark.unit
    @patch('config_extended.is_termux')
    def test_non_termux_default_timeouts(self, mock_is_termux):
        """Test timeouts por defecto en entorno no-Termux"""
        # Simular entorno no-Termux
        mock_is_termux.return_value = False
        
        # Usar la función _get_timeouts directamente
        from config_extended import _get_timeouts
        timeouts = _get_timeouts()
        
        # Verificar timeouts por defecto
        assert timeouts['REQUEST_TIMEOUT'] == 30
        assert timeouts['CONNECT_TIMEOUT'] == 5
        assert timeouts['READ_TIMEOUT'] == 30
    
    @pytest.mark.unit
    def test_termux_optimizations_config(self):
        """Test configuración de optimizaciones Termux"""
        from config_extended import TERMUX_OPTIMIZATIONS
        
        assert isinstance(TERMUX_OPTIMIZATIONS, dict)
        
        required_keys = [
            'max_image_size_mb', 'max_pdf_size_mb', 'max_text_chars',
            'console_width', 'enable_rich_formatting', 'use_compact_tables'
        ]
        
        for key in required_keys:
            assert key in TERMUX_OPTIMIZATIONS
        
        # Verificar valores razonables
        assert TERMUX_OPTIMIZATIONS['max_image_size_mb'] > 0
        assert TERMUX_OPTIMIZATIONS['max_pdf_size_mb'] > 0
        assert TERMUX_OPTIMIZATIONS['console_width'] > 0
    
    @pytest.mark.unit
    def test_mobile_network_config(self):
        """Test configuración de red móvil"""
        from config_extended import MOBILE_NETWORK_CONFIG
        
        assert isinstance(MOBILE_NETWORK_CONFIG, dict)
        
        required_keys = [
            'retry_attempts', 'retry_delay', 'chunk_size', 'stream_timeout'
        ]
        
        for key in required_keys:
            assert key in MOBILE_NETWORK_CONFIG
        
        # Verificar valores razonables
        assert MOBILE_NETWORK_CONFIG['retry_attempts'] > 0
        assert MOBILE_NETWORK_CONFIG['retry_delay'] > 0
        assert MOBILE_NETWORK_CONFIG['chunk_size'] > 0
        assert MOBILE_NETWORK_CONFIG['stream_timeout'] > 0


class TestSplitChatConfiguration:
    """Tests para configuración de split chat"""
    
    @pytest.mark.unit
    def test_split_chat_config_structure(self):
        """Test estructura de configuración de split chat"""
        from config_extended import SPLIT_CHAT_CONFIG
        
        assert isinstance(SPLIT_CHAT_CONFIG, dict)
        
        required_keys = [
            'base_port', 'max_splits', 'auto_merge_timeout', 'context_limit'
        ]
        
        for key in required_keys:
            assert key in SPLIT_CHAT_CONFIG
        
        # Verificar valores razonables
        assert SPLIT_CHAT_CONFIG['base_port'] > 1000
        assert SPLIT_CHAT_CONFIG['max_splits'] > 0
        assert SPLIT_CHAT_CONFIG['auto_merge_timeout'] > 0
        assert SPLIT_CHAT_CONFIG['context_limit'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
