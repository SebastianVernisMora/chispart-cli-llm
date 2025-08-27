"""
Test de integración para los nuevos módulos agregados
Verifica que api_client, utils, termux_utils y config_extended funcionen correctamente
"""
import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Agregar el directorio actual al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test que todos los módulos nuevos se importen correctamente"""
    try:
        import api_client
        import utils
        import termux_utils
        import config_extended
        print("✅ Todos los módulos se importaron correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False

def test_config_extended():
    """Test de configuración extendida"""
    try:
        from config_extended import (
            get_api_config, get_available_models, get_default_model,
            AVAILABLE_APIS, DEFAULT_API, get_vision_supported_apis
        )
        
        # Test configuración básica
        config = get_api_config('blackbox')
        assert 'name' in config
        assert 'base_url' in config
        print(f"✅ Configuración blackbox: {config['name']}")
        
        # Test modelos disponibles
        models = get_available_models('blackbox')
        assert len(models) > 0
        print(f"✅ Modelos blackbox disponibles: {len(models)}")
        
        # Test modelo por defecto
        default_model = get_default_model('blackbox')
        assert default_model in models
        print(f"✅ Modelo por defecto blackbox: {default_model}")
        
        # Test APIs con visión
        vision_apis = get_vision_supported_apis()
        assert len(vision_apis) > 0
        print(f"✅ APIs con visión: {vision_apis}")
        
        return True
    except Exception as e:
        print(f"❌ Error en config_extended: {e}")
        return False

def test_utils():
    """Test de utilidades"""
    try:
        from utils import (
            is_supported_image, is_supported_pdf, format_file_size,
            validate_api_key_format, validate_url
        )
        
        # Test validación de imágenes
        assert is_supported_image('test.jpg') == True
        assert is_supported_image('test.txt') == False
        print("✅ Validación de imágenes funciona")
        
        # Test validación de PDFs
        assert is_supported_pdf('test.pdf') == True
        assert is_supported_pdf('test.jpg') == False
        print("✅ Validación de PDFs funciona")
        
        # Test formateo de tamaño
        size_str = format_file_size(1024)
        assert 'KB' in size_str
        print(f"✅ Formateo de tamaño: {size_str}")
        
        # Test validación de API keys
        assert validate_api_key_format('sk-test123456789', 'blackbox') == True
        assert validate_api_key_format('invalid', 'blackbox') == False
        print("✅ Validación de API keys funciona")
        
        # Test validación de URLs
        assert validate_url('https://api.blackbox.ai') == True
        assert validate_url('invalid-url') == False
        print("✅ Validación de URLs funciona")
        
        return True
    except Exception as e:
        print(f"❌ Error en utils: {e}")
        return False

def test_termux_utils():
    """Test de utilidades Termux"""
    try:
        from termux_utils import (
            is_termux, get_mobile_optimized_timeouts, get_mobile_file_limits,
            get_optimized_console_width
        )
        
        # Test detección de Termux
        termux_detected = is_termux()
        print(f"✅ Termux detectado: {termux_detected}")
        
        # Test timeouts optimizados
        timeouts = get_mobile_optimized_timeouts()
        assert 'connect_timeout' in timeouts
        assert 'read_timeout' in timeouts
        print(f"✅ Timeouts optimizados: {timeouts}")
        
        # Test límites de archivos
        limits = get_mobile_file_limits()
        assert 'max_image_size_mb' in limits
        print(f"✅ Límites de archivos: {limits}")
        
        # Test ancho de consola
        width = get_optimized_console_width()
        assert isinstance(width, int)
        assert width > 0
        print(f"✅ Ancho de consola: {width}")
        
        return True
    except Exception as e:
        print(f"❌ Error en termux_utils: {e}")
        return False

def test_api_client():
    """Test del cliente API"""
    try:
        from api_client import UniversalAPIClient, APIError
        
        # Test inicialización del cliente
        client = UniversalAPIClient(
            api_key="sk-test123456789",
            base_url="https://api.blackbox.ai",
            api_name="blackbox"
        )
        
        assert client.api_key == "sk-test123456789"
        assert client.api_name == "blackbox"
        print("✅ Cliente API inicializado correctamente")
        
        # Test validación de conexión (mock)
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"total_tokens": 10}
            }
            mock_post.return_value = mock_response
            
            validation = client.validate_connection()
            assert validation['valid'] == True
            print("✅ Validación de conexión funciona")
        
        return True
    except Exception as e:
        print(f"❌ Error en api_client: {e}")
        return False

def test_app_integration():
    """Test de integración con la aplicación Flask"""
    try:
        from app import ChispartMobileApp
        
        # Test inicialización de la app
        app_instance = ChispartMobileApp()
        assert app_instance.app is not None
        print("✅ Aplicación Flask inicializada")
        
        # Test configuración
        config = app_instance._get_client_config()
        assert isinstance(config, dict)
        print("✅ Configuración del cliente obtenida")
        
        # Test información de proveedores
        providers = app_instance._get_api_providers_info()
        assert isinstance(providers, list)
        assert len(providers) > 0
        print(f"✅ Proveedores de API: {len(providers)} encontrados")
        
        return True
    except Exception as e:
        print(f"❌ Error en integración de app: {e}")
        return False

def run_all_tests():
    """Ejecuta todos los tests de integración"""
    print("🧪 Iniciando tests de integración para nuevos módulos...")
    print("=" * 60)
    
    tests = [
        ("Importación de módulos", test_imports),
        ("Configuración extendida", test_config_extended),
        ("Utilidades", test_utils),
        ("Utilidades Termux", test_termux_utils),
        ("Cliente API", test_api_client),
        ("Integración de aplicación", test_app_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests pasaron ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        return True
    else:
        print("⚠️  Algunos tests fallaron. Revisar los errores arriba.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
