"""
Tests comprehensivos para chispart_dev_agent_v3.py
Incluye tests unitarios y de integración para el CLI principal
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, call
from click.testing import CliRunner
import tempfile
import json

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar el módulo principal
import chispart_dev_agent_v3 as cli_module
from chispart_dev_agent_v3 import (
    cli, validate_api_key, create_text_message, 
    create_image_message, create_pdf_message
)


class TestValidateApiKey:
    """Tests para la función validate_api_key"""
    
    @pytest.mark.unit
    def test_validate_api_key_success(self, mock_env_vars):
        """Test validación exitosa de API key"""
        with patch('chispart_dev_agent_v3.get_api_config') as mock_config:
            mock_config.return_value = {
                'name': 'Test API',
                'api_key': 'valid_key_123'
            }
            
            result = validate_api_key('chispart')
            
            assert result['name'] == 'Test API'
            assert result['api_key'] == 'valid_key_123'
    
    @pytest.mark.unit
    def test_validate_api_key_missing(self, mock_env_vars):
        """Test validación con API key faltante"""
        with patch('chispart_dev_agent_v3.get_api_config') as mock_config, \
             patch('chispart_dev_agent_v3.console') as mock_console, \
             pytest.raises(SystemExit):
            
            mock_config.return_value = {
                'name': 'Test API',
                'api_key': ''
            }
            
            validate_api_key('chispart')
            
            # Verificar que se mostró el error
            mock_console.print.assert_called()
    
    @pytest.mark.unit
    def test_validate_api_key_placeholder(self, mock_env_vars):
        """Test validación con placeholder de API key"""
        with patch('chispart_dev_agent_v3.get_api_config') as mock_config, \
             patch('chispart_dev_agent_v3.console') as mock_console, \
             pytest.raises(SystemExit):
            
            mock_config.return_value = {
                'name': 'Test API',
                'api_key': 'your_api_key_here'
            }
            
            validate_api_key('chispart')
            
            mock_console.print.assert_called()


class TestMessageCreation:
    """Tests para funciones de creación de mensajes"""
    
    @pytest.mark.unit
    def test_create_text_message(self):
        """Test creación de mensaje de texto"""
        content = "Hola, ¿cómo estás?"
        result = create_text_message(content)
        
        expected = {
            "role": "user",
            "content": content
        }
        
        assert result == expected
    
    @pytest.mark.unit
    def test_create_image_message_success(self, sample_image_file):
        """Test creación exitosa de mensaje con imagen"""
        with patch('chispart_dev_agent_v3.create_image_data_url') as mock_create_url:
            mock_create_url.return_value = "data:image/jpeg;base64,fake_data"
            
            text = "Analiza esta imagen"
            result = create_image_message(text, sample_image_file)
            
            assert result["role"] == "user"
            assert isinstance(result["content"], list)
            assert len(result["content"]) == 2
            assert result["content"][0]["type"] == "text"
            assert result["content"][0]["text"] == text
            assert result["content"][1]["type"] == "image_url"
    
    @pytest.mark.unit
    def test_create_image_message_error(self, sample_image_file):
        """Test error en creación de mensaje con imagen"""
        with patch('chispart_dev_agent_v3.create_image_data_url') as mock_create_url:
            mock_create_url.side_effect = Exception("Error procesando imagen")
            
            with pytest.raises(Exception) as exc_info:
                create_image_message("Test", sample_image_file)
            
            assert "Error procesando imagen" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_create_pdf_message_success(self, sample_pdf_file):
        """Test creación exitosa de mensaje con PDF"""
        with patch('chispart_dev_agent_v3.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Contenido del PDF de prueba"
            
            text = "Analiza este documento"
            result = create_pdf_message(text, sample_pdf_file)
            
            assert result["role"] == "user"
            assert "Contenido del PDF de prueba" in result["content"]
            assert text in result["content"]
    
    @pytest.mark.unit
    def test_create_pdf_message_long_content(self, sample_pdf_file):
        """Test creación de mensaje con PDF de contenido largo"""
        with patch('chispart_dev_agent_v3.extract_text_from_pdf') as mock_extract:
            # Simular contenido muy largo
            long_content = "A" * 150000  # Más de 100,000 caracteres
            mock_extract.return_value = long_content
            
            result = create_pdf_message("Test", sample_pdf_file)
            
            # Verificar que el contenido fue truncado
            assert "[... CONTENIDO TRUNCADO ...]" in result["content"]
            assert len(result["content"]) < len(long_content) + 1000


class TestCLICommands:
    """Tests para comandos CLI principales"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.runner = CliRunner()
    
    @pytest.mark.cli
    def test_cli_help(self):
        """Test comando de ayuda principal"""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Chispart Dev Agent v3.0" in result.output
        assert "chat" in result.output
        assert "execute" in result.output
    
    @pytest.mark.cli
    def test_version_command(self):
        """Test comando version"""
        with patch('chispart_dev_agent_v3.console') as mock_console:
            result = self.runner.invoke(cli, ['version'])
            
            assert result.exit_code == 0
            mock_console.print.assert_called()
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.validate_api_key')
    @patch('chispart_dev_agent_v3.get_available_models')
    @patch('chispart_dev_agent_v3.get_default_model')
    @patch('chispart_dev_agent_v3.UniversalAPIClient')
    @patch('chispart_dev_agent_v3.console')
    def test_chat_command_success(self, mock_console, mock_client_class, 
                                 mock_default_model, mock_available_models, 
                                 mock_validate):
        """Test comando chat exitoso"""
        # Configurar mocks
        mock_validate.return_value = {
            'name': 'Test API',
            'api_key': 'test_key',
            'base_url': 'https://test.api'
        }
        mock_available_models.return_value = {'gpt-4': 'test-model-id'}
        mock_default_model.return_value = 'gpt-4'
        
        mock_client = MagicMock()
        mock_client.chat_completions.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_client.extract_response_content.return_value = 'Test response'
        mock_client.get_usage_info.return_value = {'total_tokens': 30}
        mock_client_class.return_value = mock_client
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['chat', 'Hola'])
        
        assert result.exit_code == 0
        mock_client.chat_completions.assert_called_once()
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.validate_api_key')
    def test_chat_command_invalid_api(self, mock_validate):
        """Test comando chat con API inválida"""
        mock_validate.side_effect = SystemExit(1)
        
        result = self.runner.invoke(cli, ['chat', 'Hola'])
        
        assert result.exit_code == 1
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.security_manager')
    @patch('chispart_dev_agent_v3.subprocess.run')
    @patch('chispart_dev_agent_v3.console')
    def test_execute_command_safe_success(self, mock_console, mock_subprocess, 
                                        mock_security):
        """Test ejecución segura de comando exitosa"""
        # Configurar mock de seguridad
        mock_validation = MagicMock()
        mock_validation.is_allowed = True
        mock_security.validate_command.return_value = mock_validation
        
        # Configurar mock de subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        result = self.runner.invoke(cli, ['execute', 'ls -la', '--safe'])
        
        assert result.exit_code == 0
        mock_security.validate_command.assert_called_once_with('ls -la')
        mock_subprocess.assert_called_once()
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.security_manager')
    @patch('chispart_dev_agent_v3.console')
    def test_execute_command_blocked(self, mock_console, mock_security):
        """Test ejecución de comando bloqueado por seguridad"""
        # Configurar mock de seguridad para bloquear comando
        mock_validation = MagicMock()
        mock_validation.is_allowed = False
        mock_validation.reason = "Comando peligroso"
        mock_security.validate_command.return_value = mock_validation
        
        result = self.runner.invoke(cli, ['execute', 'rm -rf /', '--safe'])
        
        assert result.exit_code == 0  # No falla, solo no ejecuta
        mock_security.validate_command.assert_called_once()
        mock_console.print.assert_called()
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.profile_manager')
    def test_perfiles_command(self, mock_profile_manager):
        """Test comando perfiles"""
        result = self.runner.invoke(cli, ['perfiles'])
        
        assert result.exit_code == 0
        mock_profile_manager.display_profiles_table.assert_called_once()
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.team_manager')
    def test_equipos_command(self, mock_team_manager):
        """Test comando equipos"""
        result = self.runner.invoke(cli, ['equipos'])
        
        assert result.exit_code == 0
        mock_team_manager.display_teams_table.assert_called_once()
    
    @pytest.mark.cli
    @patch('chispart_dev_agent_v3.get_api_config')
    @patch('chispart_dev_agent_v3.get_available_models')
    @patch('chispart_dev_agent_v3.console')
    def test_modelos_command(self, mock_console, mock_available_models, 
                           mock_api_config):
        """Test comando modelos"""
        mock_api_config.return_value = {'name': 'Test API'}
        mock_available_models.return_value = {
            'gpt-4': 'model-id-1',
            'claude-3.5-sonnet': 'model-id-2'
        }
        
        result = self.runner.invoke(cli, ['modelos'])
        
        assert result.exit_code == 0
        mock_console.print.assert_called()


class TestCLIIntegration:
    """Tests de integración para flujos completos del CLI"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.runner = CliRunner()
    
    @pytest.mark.integration
    @patch('chispart_dev_agent_v3.validate_api_key')
    @patch('chispart_dev_agent_v3.get_available_models')
    @patch('chispart_dev_agent_v3.get_default_model')
    @patch('chispart_dev_agent_v3.profile_manager')
    @patch('chispart_dev_agent_v3.UniversalAPIClient')
    @patch('chispart_dev_agent_v3.save_conversation_history')
    def test_chat_with_profile_integration(self, mock_save_history, mock_client_class,
                                         mock_profile_manager, mock_default_model,
                                         mock_available_models, mock_validate):
        """Test integración completa de chat con perfil"""
        # Configurar mocks
        mock_validate.return_value = {
            'name': 'Test API',
            'api_key': 'test_key',
            'base_url': 'https://test.api'
        }
        mock_available_models.return_value = {'gpt-4': 'test-model-id'}
        mock_default_model.return_value = 'gpt-4'
        
        # Mock del profile manager
        mock_profile_manager.profiles = {'backend': 'Backend Developer'}
        
        # Crear un mock object con atributos en lugar de diccionario
        mock_profile_info = MagicMock()
        mock_profile_info.name = 'Backend Developer'
        mock_profile_info.system_prompt = 'Eres un desarrollador backend experto'
        mock_profile_info.preferred_models = ['gpt-4']
        
        mock_profile_manager.get_profile.return_value = mock_profile_info
        
        # Mock del cliente API
        mock_client = MagicMock()
        mock_client.chat_completions.return_value = {
            'choices': [{'message': {'content': 'Respuesta del backend'}}]
        }
        mock_client.extract_response_content.return_value = 'Respuesta del backend'
        mock_client.get_usage_info.return_value = {'total_tokens': 45}
        mock_client_class.return_value = mock_client
        
        # Ejecutar comando con perfil
        result = self.runner.invoke(cli, [
            'chat', 'Crea una API REST', '--profile', 'backend'
        ])
        
        assert result.exit_code == 0
        
        # Verificar que se usó el perfil
        mock_profile_manager.get_profile.assert_called_with('backend')
        
        # Verificar que se guardó el historial
        mock_save_history.assert_called_once()
        
        # Verificar que el mensaje incluye el system prompt
        call_args = mock_client.chat_completions.call_args[0]
        messages = call_args[0]
        assert 'Eres un desarrollador backend experto' in messages[0]['content']
    
    @pytest.mark.integration
    @patch('chispart_dev_agent_v3.security_manager')
    @patch('chispart_dev_agent_v3.subprocess.run')
    @patch('chispart_dev_agent_v3.time.time')
    def test_execute_command_with_timeout(self, mock_time, mock_subprocess, 
                                        mock_security):
        """Test ejecución de comando con timeout"""
        # Configurar mocks
        mock_validation = MagicMock()
        mock_validation.is_allowed = True
        mock_security.validate_command.return_value = mock_validation
        
        # Simular timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired('test', 5)
        mock_time.side_effect = [0, 5]  # Simular tiempo transcurrido
        
        with patch('chispart_dev_agent_v3.console') as mock_console:
            result = self.runner.invoke(cli, [
                'execute', 'sleep 10', '--safe', '--timeout', '5'
            ])
            
            assert result.exit_code == 0
            mock_console.print.assert_called()
            # Verificar que se mostró mensaje de timeout
            timeout_calls = [call for call in mock_console.print.call_args_list 
                           if 'timeout' in str(call).lower()]
            assert len(timeout_calls) > 0


class TestErrorHandling:
    """Tests para manejo de errores"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.runner = CliRunner()
    
    @pytest.mark.unit
    @patch('chispart_dev_agent_v3.validate_api_key')
    @patch('chispart_dev_agent_v3.get_available_models')
    @patch('chispart_dev_agent_v3.UniversalAPIClient')
    def test_chat_api_error_handling(self, mock_client_class, mock_available_models, 
                                   mock_validate):
        """Test manejo de errores de API en chat"""
        from api_client import APIError
        
        # Configurar mocks
        mock_validate.return_value = {
            'name': 'Test API',
            'api_key': 'test_key',
            'base_url': 'https://test.api'
        }
        mock_available_models.return_value = {'gpt-4': 'test-model-id'}
        
        # Configurar error de API
        mock_client = MagicMock()
        mock_client.chat_completions.side_effect = APIError(
            "API Error", "test_api", 401
        )
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(cli, ['chat', 'Test message'])
        
        assert result.exit_code == 1
    
    @pytest.mark.unit
    def test_invalid_command_arguments(self):
        """Test argumentos inválidos en comandos"""
        result = self.runner.invoke(cli, ['chat'])  # Sin mensaje
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output


# Importar subprocess para el test de timeout
import subprocess

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
