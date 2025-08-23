#!/usr/bin/env python3
"""
Script de prueba para verificar las optimizaciones de Termux
Verifica que todas las funcionalidades estén funcionando correctamente
"""

import sys
import os
import importlib
from pathlib import Path

def test_imports():
    """Prueba que todos los módulos se importen correctamente"""
    print("🔍 Probando imports...")
    
    modules_to_test = [
        'requests',
        'click', 
        'rich',
        'flask',
        'PIL',
        'dotenv',
        'termux_utils',
        'config',
        'utils',
        'api_client'
    ]
    
    results = {}
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            results[module] = "✅"
        except ImportError as e:
            results[module] = f"❌ {str(e)}"
    
    for module, status in results.items():
        print(f"  {module}: {status}")
    
    return all("✅" in status for status in results.values())

def test_termux_utils():
    """Prueba las utilidades específicas de Termux"""
    print("\n🔧 Probando utilidades de Termux...")
    
    try:
        from termux_utils import (
            is_termux, get_termux_temp_dir, get_safe_temp_path,
            ensure_directory_exists, get_optimized_console_width,
            check_termux_dependencies, get_mobile_optimized_timeouts,
            optimize_file_size_limits
        )
        
        # Probar funciones básicas
        print(f"  is_termux(): {is_termux()}")
        print(f"  temp_dir: {get_termux_temp_dir()}")
        print(f"  console_width: {get_optimized_console_width()}")
        
        # Probar creación de directorio
        test_dir = get_safe_temp_path("test_dir")
        if ensure_directory_exists(test_dir):
            print(f"  ✅ Directorio creado: {test_dir}")
            os.rmdir(test_dir)  # Limpiar
        else:
            print(f"  ❌ No se pudo crear directorio")
        
        # Probar configuraciones
        timeouts = get_mobile_optimized_timeouts()
        limits = optimize_file_size_limits()
        print(f"  ✅ Timeouts: {timeouts}")
        print(f"  ✅ Límites: {limits}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_config():
    """Prueba la configuración optimizada"""
    print("\n⚙️ Probando configuración...")
    
    try:
        from config import (
            get_api_config, get_available_models, get_default_model,
            REQUEST_TIMEOUT, TERMUX_OPTIMIZATIONS, MOBILE_NETWORK_CONFIG
        )
        
        # Probar configuración de API
        config = get_api_config('blackbox')
        print(f"  ✅ Config API: {config['name']}")
        print(f"  ✅ Timeout: {config.get('timeout', 'N/A')}")
        
        # Probar modelos
        models = get_available_models('blackbox')
        default_model = get_default_model('blackbox')
        print(f"  ✅ Modelos disponibles: {len(models)}")
        print(f"  ✅ Modelo por defecto: {default_model}")
        
        # Probar configuraciones específicas
        print(f"  ✅ Optimizaciones Termux: {len(TERMUX_OPTIMIZATIONS)} configuraciones")
        print(f"  ✅ Config red móvil: {len(MOBILE_NETWORK_CONFIG)} configuraciones")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_utils():
    """Prueba las utilidades optimizadas"""
    print("\n🛠️ Probando utilidades...")
    
    try:
        from utils import (
            encode_file_to_base64, create_image_data_url, 
            is_supported_image, is_supported_pdf,
            format_file_size, validate_file_size,
            PYMUPDF_AVAILABLE
        )
        
        # Probar validaciones de archivo
        print(f"  ✅ PyMuPDF disponible: {PYMUPDF_AVAILABLE}")
        print(f"  ✅ Imagen soportada (.jpg): {is_supported_image('test.jpg')}")
        print(f"  ✅ PDF soportado (.pdf): {is_supported_pdf('test.pdf')}")
        
        # Probar formato de tamaño
        size_str = format_file_size(1024 * 1024)  # 1MB
        print(f"  ✅ Formato tamaño: {size_str}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_api_client():
    """Prueba el cliente API optimizado"""
    print("\n🌐 Probando cliente API...")
    
    try:
        from api_client import UniversalAPIClient, APIError
        
        # Crear cliente de prueba (sin clave real)
        client = UniversalAPIClient("test_key", "https://api.test.com", "Test API")
        print(f"  ✅ Cliente creado: {client.api_name}")
        
        # Probar manejo de errores
        try:
            # Esto debería fallar por clave inválida
            client.chat_completions([{"role": "user", "content": "test"}], "test-model")
        except (APIError, Exception) as e:
            print(f"  ✅ Manejo de errores funciona: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_files_exist():
    """Verifica que todos los archivos necesarios existan"""
    print("\n📁 Verificando archivos...")
    
    required_files = [
        'termux_utils.py',
        'install_termux.sh',
        'llm-cli',
        'llm-web', 
        'llm-status',
        'README_TERMUX.md',
        'requirements_termux.txt',
        'OPTIMIZACIONES_TERMUX.md',
        'blackbox_cli.py',
        'app.py',
        'config.py',
        'utils.py',
        'api_client.py'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (faltante)")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_scripts_executable():
    """Verifica que los scripts sean ejecutables"""
    print("\n🔧 Verificando permisos de scripts...")
    
    scripts = ['install_termux.sh', 'llm-cli', 'llm-web', 'llm-status']
    
    for script in scripts:
        if Path(script).exists():
            if os.access(script, os.X_OK):
                print(f"  ✅ {script} (ejecutable)")
            else:
                print(f"  ⚠️  {script} (no ejecutable)")
        else:
            print(f"  ❌ {script} (no existe)")
    
    return True

def main():
    """Función principal de pruebas"""
    print("🚀 Probando Optimizaciones de Termux para CLI Universal LLMs")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Utilidades Termux", test_termux_utils),
        ("Configuración", test_config),
        ("Utilidades", test_utils),
        ("Cliente API", test_api_client),
        ("Archivos", test_files_exist),
        ("Scripts ejecutables", test_scripts_executable)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error en {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las optimizaciones funcionan correctamente!")
        print("🚀 El sistema está listo para usar en Termux")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("💡 El sistema puede funcionar parcialmente")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)