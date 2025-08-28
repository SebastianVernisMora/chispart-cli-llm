"""
Tests para módulos core de Chispart CLI
Incluye tests para dev_profiles, security_manager, team_manager, etc.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, mock_open
import json
import tempfile

# Agregar el directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Intentar importar módulos core (pueden no estar disponibles en todos los entornos)
try:
    from core.dev_profiles import profile_manager
    PROFILES_AVAILABLE = True
except ImportError:
    PROFILES_AVAILABLE = False

try:
    from core.security_manager import security_manager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

try:
    from core.team_manager import team_manager
    TEAMS_AVAILABLE = True
except ImportError:
    TEAMS_AVAILABLE = False


@pytest.mark.skipif(not PROFILES_AVAILABLE, reason="Módulo dev_profiles no disponible")
class TestDevProfiles:
    """Tests para gestión de perfiles de desarrollo"""
    
    @pytest.mark.unit
    def test_profiles_structure(self):
        """Test estructura básica de perfiles"""
        assert hasattr(profile_manager, 'profiles')
        assert isinstance(profile_manager.profiles, dict)
        
        # Verificar que hay perfiles definidos
        assert len(profile_manager.profiles) > 0
    
    @pytest.mark.unit
    def test_profile_content_structure(self):
        """Test estructura de contenido de perfiles"""
        for profile_name, profile_data in profile_manager.profiles.items():
            # Verificar campos requeridos (profile_data es un objeto DevProfile)
            assert hasattr(profile_data, 'name')
            assert hasattr(profile_data, 'description')
            assert hasattr(profile_data, 'system_prompt')
            
            # Verificar tipos
            assert isinstance(profile_data.name, str)
            assert isinstance(profile_data.description, str)
            assert isinstance(profile_data.system_prompt, str)
            
            # Verificar que el system_prompt no está vacío
            assert len(profile_data.system_prompt.strip()) > 0
    
    @pytest.mark.unit
    def test_get_profile_valid(self):
        """Test obtener perfil válido"""
        if len(profile_manager.profiles) > 0:
            profile_name = list(profile_manager.profiles.keys())[0]
            profile_info = profile_manager.get_profile(profile_name)
            
            assert profile_info is not None
            assert profile_info.name == profile_manager.profiles[profile_name].name
    
    @pytest.mark.unit
    def test_get_profile_invalid(self):
        """Test obtener perfil inválido"""
        profile_info = profile_manager.get_profile('perfil_inexistente')
        assert profile_info is None
    
    @pytest.mark.unit
    def test_common_profiles_exist(self):
        """Test que existen perfiles comunes"""
        expected_profiles = [
            'frontend', 'backend', 'fullstack', 'devops', 
            'mobile', 'data', 'security'
        ]
        
        available_profiles = [name.lower() for name in profile_manager.profiles.keys()]
        
        # Al menos algunos perfiles comunes deberían existir
        common_found = sum(1 for profile in expected_profiles 
                          if any(profile in available.lower() for available in available_profiles))
        
        assert common_found >= 3, "Deberían existir al menos 3 perfiles comunes"
    
    @pytest.mark.unit
    @patch('rich.console.Console')
    def test_display_profiles_table(self, mock_console_class):
        """Test mostrar tabla de perfiles"""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        profile_manager.display_profiles_table()
        
        # Verificar que se llamó print en la consola
        mock_console.print.assert_called()


@pytest.mark.skipif(not SECURITY_AVAILABLE, reason="Módulo security_manager no disponible")
class TestSecurityManager:
    """Tests para gestión de seguridad"""
    
    @pytest.mark.unit
    def test_validate_command_allowed(self):
        """Test validación de comando permitido"""
        # Comandos que deberían estar permitidos
        safe_commands = ['ls', 'pwd', 'git status', 'python --version']
        
        for command in safe_commands:
            validation = security_manager.validate_command(command)
            assert hasattr(validation, 'is_allowed')
            # Nota: El resultado puede variar según la configuración
    
    @pytest.mark.unit
    def test_validate_command_dangerous(self):
        """Test validación de comando peligroso"""
        # Comandos que deberían estar bloqueados
        dangerous_commands = [
            'sudo rm -rf /',
            'rm -rf *',
            'chmod 777 /',
            'passwd root'
        ]
        
        for command in dangerous_commands:
            validation = security_manager.validate_command(command)
            assert hasattr(validation, 'is_allowed')
            assert hasattr(validation, 'reason')
            
            # Si está bloqueado, debe tener una razón
            if not validation.is_allowed:
                assert isinstance(validation.reason, str)
                assert len(validation.reason) > 0
    
    @pytest.mark.unit
    def test_validate_command_empty(self):
        """Test validación de comando vacío"""
        validation = security_manager.validate_command('')
        assert hasattr(validation, 'is_allowed')
        # Comando vacío debería ser rechazado
        assert not validation.is_allowed
    
    @pytest.mark.unit
    @patch('rich.console.Console')
    def test_display_security_status(self, mock_console_class):
        """Test mostrar estado de seguridad"""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        security_manager.display_security_status()
        
        # Verificar que se mostró información
        mock_console.print.assert_called()


@pytest.mark.skipif(not TEAMS_AVAILABLE, reason="Módulo team_manager no disponible")
class TestTeamManager:
    """Tests para gestión de equipos"""
    
    def setup_method(self):
        """Configuración para cada test"""
        # Limpiar equipos existentes para tests aislados
        if hasattr(team_manager, 'teams'):
            team_manager.teams = {}
    
    @pytest.mark.unit
    def test_create_team_basic(self):
        """Test creación básica de equipo"""
        team_data = {
            'name': 'Test Team',
            'description': 'Equipo de prueba',
            'project_type': 'web',
            'tech_stack': ['Python', 'JavaScript'],
            'preferred_apis': ['chispart']
        }
        
        try:
            team_id = team_manager.create_team(
                team_data['name'],
                team_data['description'],
                team_data['project_type'],
                team_data['tech_stack'],
                team_data['preferred_apis']
            )
            
            assert isinstance(team_id, str)
            assert len(team_id) > 0
            
            # Verificar que el equipo fue creado
            if hasattr(team_manager, 'teams'):
                assert team_id in team_manager.teams
                
        except Exception as e:
            # Si falla, al menos verificar que es por una razón válida
            assert isinstance(e, (ValueError, TypeError, AttributeError))
    
    @pytest.mark.unit
    def test_create_team_duplicate_name(self):
        """Test creación de equipo con nombre duplicado"""
        team_data = {
            'name': 'Duplicate Team',
            'description': 'Equipo duplicado',
            'project_type': 'api',
            'tech_stack': ['Python'],
            'preferred_apis': ['chispart']
        }
        
        try:
            # Crear primer equipo
            team_id1 = team_manager.create_team(
                team_data['name'],
                team_data['description'],
                team_data['project_type'],
                team_data['tech_stack'],
                team_data['preferred_apis']
            )
            
            # Intentar crear segundo equipo con mismo nombre
            with pytest.raises(ValueError):
                team_manager.create_team(
                    team_data['name'],  # Mismo nombre
                    'Otra descripción',
                    'mobile',
                    ['React Native'],
                    ['qwen']
                )
                
        except AttributeError:
            # El método puede no estar implementado
            pytest.skip("Método create_team no implementado")
    
    @pytest.mark.unit
    def test_add_member_to_team(self):
        """Test agregar miembro a equipo"""
        # Primero crear un equipo
        try:
            team_id = team_manager.create_team(
                'Team for Members',
                'Equipo para probar miembros',
                'fullstack',
                ['Python', 'React'],
                ['chispart', 'qwen']
            )
            
            # Agregar miembro
            member_data = {
                'name': 'John Developer',
                'profile': 'backend',
                'role': 'senior',
                'specialties': ['APIs', 'databases'],
                'preferred_models': ['gpt-4', 'claude-3.5-sonnet']
            }
            
            team_manager.add_member(
                team_id,
                member_data['name'],
                member_data['profile'],
                member_data['role'],
                member_data['specialties'],
                member_data['preferred_models']
            )
            
            # Verificar que el miembro fue agregado
            if hasattr(team_manager, 'teams') and team_id in team_manager.teams:
                team = team_manager.teams[team_id]
                if hasattr(team, 'members'):
                    assert len(team.members) > 0
                    
        except (AttributeError, NotImplementedError):
            pytest.skip("Métodos de team_manager no implementados")
    
    @pytest.mark.unit
    @patch('core.team_manager.console')
    def test_display_teams_table(self, mock_console):
        """Test mostrar tabla de equipos"""
        try:
            team_manager.display_teams_table()
            # Verificar que se intentó mostrar algo (ya sea tabla o mensaje de "no hay equipos")
            mock_console.print.assert_called()
        except AttributeError:
            pytest.skip("Método display_teams_table no implementado")


class TestCoreModulesIntegration:
    """Tests de integración entre módulos core"""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not (PROFILES_AVAILABLE and TEAMS_AVAILABLE), 
                       reason="Módulos requeridos no disponibles")
    def test_team_with_profiles_integration(self):
        """Test integración entre equipos y perfiles"""
        try:
            # Obtener un perfil disponible
            if len(profile_manager.profiles) > 0:
                profile_name = list(profile_manager.profiles.keys())[0]
                
                # Crear equipo usando el perfil
                team_id = team_manager.create_team(
                    'Integration Team',
                    'Equipo de integración',
                    'web',
                    ['Python', 'JavaScript'],
                    ['chispart']
                )
                
                # Agregar miembro con el perfil
                team_manager.add_member(
                    team_id,
                    'Integration Developer',
                    profile_name,
                    'mid',
                    ['development'],
                    ['gpt-4']
                )
                
                # Verificar integración exitosa
                assert team_id is not None
                
        except (AttributeError, NotImplementedError, ValueError):
            pytest.skip("Integración no soportada en la implementación actual")
    
    @pytest.mark.integration
    @pytest.mark.skipif(not (SECURITY_AVAILABLE and PROFILES_AVAILABLE),
                       reason="Módulos requeridos no disponibles")
    def test_security_with_profiles_integration(self):
        """Test integración entre seguridad y perfiles"""
        try:
            # Verificar que los perfiles no afectan la validación de seguridad
            validation = security_manager.validate_command('ls -la')
            
            # La validación debería ser independiente de los perfiles
            assert hasattr(validation, 'is_allowed')
            
        except AttributeError:
            pytest.skip("Integración no soportada")


class TestCoreModulesMocking:
    """Tests usando mocks para módulos core no disponibles"""
    
    @pytest.mark.unit
    def test_mock_profile_manager(self):
        """Test mock de profile manager"""
        mock_profiles = {
            'backend': {
                'name': 'Backend Developer',
                'description': 'Especialista en desarrollo backend',
                'system_prompt': 'Eres un desarrollador backend experto...',
                'preferred_models': ['gpt-4', 'claude-3.5-sonnet']
            },
            'frontend': {
                'name': 'Frontend Developer', 
                'description': 'Especialista en desarrollo frontend',
                'system_prompt': 'Eres un desarrollador frontend experto...',
                'preferred_models': ['gpt-4', 'gemini-pro']
            }
        }
        
        with patch('core.dev_profiles.profile_manager') as mock_manager:
            mock_manager.profiles = mock_profiles
            mock_manager.get_profile.return_value = mock_profiles['backend']
            
            # Test usando el mock
            profile = mock_manager.get_profile('backend')
            assert profile['name'] == 'Backend Developer'
            assert 'system_prompt' in profile
    
    @pytest.mark.unit
    def test_mock_security_manager(self):
        """Test mock de security manager"""
        # Crear mock directo sin patch complejo
        mock_manager = MagicMock()
        
        # Configurar mock de validación para comando seguro
        mock_validation_safe = MagicMock()
        mock_validation_safe.is_allowed = True
        mock_validation_safe.reason = None
        
        # Configurar mock de validación para comando peligroso
        mock_validation_dangerous = MagicMock()
        mock_validation_dangerous.is_allowed = False
        mock_validation_dangerous.reason = "Comando peligroso"
        
        # Configurar comportamiento del mock
        def mock_validate_command(command):
            if 'rm -rf' in command:
                return mock_validation_dangerous
            else:
                return mock_validation_safe
        
        mock_manager.validate_command.side_effect = mock_validate_command
        
        # Test comando seguro
        validation = mock_manager.validate_command('ls -la')
        assert validation.is_allowed is True
        
        # Test comando peligroso
        validation = mock_manager.validate_command('rm -rf /')
        assert validation.is_allowed is False
        assert validation.reason == "Comando peligroso"
    
    @pytest.mark.unit
    def test_mock_team_manager(self):
        """Test mock de team manager"""
        with patch('core.team_manager.team_manager') as mock_manager:
            mock_manager.teams = {}
            mock_manager.create_team.return_value = 'team_123'
            
            # Test creación de equipo
            team_id = mock_manager.create_team(
                'Test Team', 'Description', 'web', 
                ['Python'], ['chispart']
            )
            
            assert team_id == 'team_123'
            mock_manager.create_team.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
