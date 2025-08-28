#!/usr/bin/env python3
"""
Script principal para ejecutar tests de Chispart CLI
Incluye diferentes tipos de tests y opciones de configuración
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time
from datetime import datetime

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Imprime mensaje con color"""
    print(f"{color}{message}{Colors.END}")

def print_banner():
    """Imprime banner del sistema de tests"""
    print_colored("=" * 80, Colors.CYAN)
    print_colored("🧪 CHISPART CLI - SISTEMA DE TESTS COMPREHENSIVO", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 80, Colors.CYAN)
    print()

def check_dependencies():
    """Verifica que las dependencias de testing estén instaladas"""
    print_colored("🔍 Verificando dependencias de testing...", Colors.BLUE)
    
    required_packages = [
        'pytest',
        'pytest-mock',
        'pytest-cov',
        'pytest-xdist',
        'psutil',
        'memory-profiler'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_colored(f"  ✅ {package}", Colors.GREEN)
        except ImportError:
            print_colored(f"  ❌ {package}", Colors.RED)
            missing_packages.append(package)
    
    if missing_packages:
        print_colored(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}", Colors.YELLOW)
        print_colored("Instala con: pip install " + " ".join(missing_packages), Colors.YELLOW)
        return False
    
    print_colored("✅ Todas las dependencias están instaladas", Colors.GREEN)
    return True

def run_pytest_command(args, test_type=""):
    """Ejecuta comando pytest y maneja el resultado"""
    print_colored(f"\n🚀 Ejecutando {test_type}...", Colors.BLUE)
    print_colored(f"Comando: pytest {' '.join(args)}", Colors.CYAN)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(['pytest'] + args, capture_output=True, text=True)
        end_time = time.time()
        duration = end_time - start_time
        
        print_colored(f"\n📊 Resultado de {test_type}:", Colors.BOLD)
        print_colored(f"⏱️  Duración: {duration:.2f} segundos", Colors.CYAN)
        
        if result.returncode == 0:
            print_colored("✅ Tests pasaron exitosamente", Colors.GREEN)
        else:
            print_colored("❌ Algunos tests fallaron", Colors.RED)
        
        # Mostrar output
        if result.stdout:
            print_colored("\n📋 Output:", Colors.BLUE)
            print(result.stdout)
        
        if result.stderr:
            print_colored("\n⚠️  Errores:", Colors.YELLOW)
            print(result.stderr)
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print_colored("❌ pytest no encontrado. Instala con: pip install pytest", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"❌ Error ejecutando tests: {e}", Colors.RED)
        return False

def run_unit_tests(verbose=False, coverage=False):
    """Ejecuta tests unitarios"""
    args = ['-m', 'unit', 'tests/']
    
    if verbose:
        args.append('-v')
    
    if coverage:
        args.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
    
    return run_pytest_command(args, "Tests Unitarios")

def run_integration_tests(verbose=False):
    """Ejecuta tests de integración"""
    args = ['-m', 'integration', 'tests/']
    
    if verbose:
        args.append('-v')
    
    return run_pytest_command(args, "Tests de Integración")

def run_performance_tests(verbose=False):
    """Ejecuta tests de rendimiento"""
    args = ['-m', 'performance', 'tests/']
    
    if verbose:
        args.append('-v')
    
    return run_pytest_command(args, "Tests de Rendimiento")

def run_security_tests(verbose=False):
    """Ejecuta tests de seguridad"""
    args = ['-m', 'security', 'tests/']
    
    if verbose:
        args.append('-v')
    
    return run_pytest_command(args, "Tests de Seguridad")

def run_all_tests(verbose=False, coverage=False, parallel=False):
    """Ejecuta todos los tests"""
    args = ['tests/']
    
    if verbose:
        args.append('-v')
    
    if coverage:
        args.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
    
    if parallel:
        args.extend(['-n', 'auto'])  # Ejecutar en paralelo
    
    return run_pytest_command(args, "Todos los Tests")

def run_specific_test(test_file, verbose=False):
    """Ejecuta un archivo de test específico"""
    args = [f'tests/{test_file}']
    
    if verbose:
        args.append('-v')
    
    return run_pytest_command(args, f"Test Específico: {test_file}")

def run_smoke_tests():
    """Ejecuta tests básicos de smoke"""
    print_colored("🔥 Ejecutando Smoke Tests...", Colors.YELLOW)
    
    # Tests básicos para verificar que el sistema funciona
    smoke_tests = [
        'tests/test_config_extended.py::TestAPIConfiguration::test_available_apis_structure',
        'tests/test_chispart_dev_agent.py::TestAPIValidation::test_validate_api_key_valid',
        'tests/test_chispart_dev_agent.py::TestMessageCreation::test_create_text_message'
    ]
    
    args = smoke_tests + ['-v']
    return run_pytest_command(args, "Smoke Tests")

def generate_test_report():
    """Genera reporte comprehensivo de tests"""
    print_colored("\n📊 Generando reporte de tests...", Colors.PURPLE)
    
    report_args = [
        'tests/',
        '--html=test_report.html',
        '--self-contained-html',
        '--cov=.',
        '--cov-report=html:htmlcov',
        '--cov-report=xml',
        '--junit-xml=test_results.xml',
        '-v'
    ]
    
    success = run_pytest_command(report_args, "Reporte Comprehensivo")
    
    if success:
        print_colored("\n📋 Reportes generados:", Colors.GREEN)
        print_colored("  • test_report.html - Reporte HTML detallado", Colors.CYAN)
        print_colored("  • htmlcov/index.html - Reporte de cobertura", Colors.CYAN)
        print_colored("  • test_results.xml - Resultados en formato XML", Colors.CYAN)
    
    return success

def run_continuous_integration():
    """Ejecuta tests en modo CI/CD"""
    print_colored("🔄 Modo Integración Continua", Colors.PURPLE)
    
    ci_args = [
        'tests/',
        '--tb=short',
        '--strict-markers',
        '--disable-warnings',
        '-q'
    ]
    
    return run_pytest_command(ci_args, "Tests CI/CD")

def list_available_tests():
    """Lista todos los tests disponibles"""
    print_colored("📋 Tests disponibles:", Colors.BLUE)
    
    try:
        result = subprocess.run(['pytest', '--collect-only', '-q', 'tests/'], 
                              capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        else:
            print_colored("No se pudieron listar los tests", Colors.YELLOW)
            
    except Exception as e:
        print_colored(f"Error listando tests: {e}", Colors.RED)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Sistema de tests para Chispart CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py --all                    # Ejecutar todos los tests
  python run_tests.py --unit --coverage        # Tests unitarios con cobertura
  python run_tests.py --integration -v         # Tests de integración verbose
  python run_tests.py --performance            # Tests de rendimiento
  python run_tests.py --security               # Tests de seguridad
  python run_tests.py --smoke                  # Tests básicos de smoke
  python run_tests.py --file test_config.py    # Test específico
  python run_tests.py --report                 # Generar reporte completo
  python run_tests.py --ci                     # Modo CI/CD
  python run_tests.py --list                   # Listar tests disponibles
        """
    )
    
    # Tipos de tests
    parser.add_argument('--all', action='store_true', help='Ejecutar todos los tests')
    parser.add_argument('--unit', action='store_true', help='Ejecutar tests unitarios')
    parser.add_argument('--integration', action='store_true', help='Ejecutar tests de integración')
    parser.add_argument('--performance', action='store_true', help='Ejecutar tests de rendimiento')
    parser.add_argument('--security', action='store_true', help='Ejecutar tests de seguridad')
    parser.add_argument('--smoke', action='store_true', help='Ejecutar smoke tests')
    parser.add_argument('--file', help='Ejecutar archivo de test específico')
    
    # Opciones
    parser.add_argument('-v', '--verbose', action='store_true', help='Output verbose')
    parser.add_argument('--coverage', action='store_true', help='Generar reporte de cobertura')
    parser.add_argument('--parallel', action='store_true', help='Ejecutar tests en paralelo')
    
    # Utilidades
    parser.add_argument('--report', action='store_true', help='Generar reporte comprehensivo')
    parser.add_argument('--ci', action='store_true', help='Modo integración continua')
    parser.add_argument('--list', action='store_true', help='Listar tests disponibles')
    parser.add_argument('--check-deps', action='store_true', help='Verificar dependencias')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Verificar dependencias si se solicita
    if args.check_deps:
        check_dependencies()
        return
    
    # Listar tests si se solicita
    if args.list:
        list_available_tests()
        return
    
    # Verificar que pytest está disponible
    try:
        subprocess.run(['pytest', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print_colored("❌ pytest no está instalado. Instala con: pip install pytest", Colors.RED)
        return
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = True
    start_time = time.time()
    
    # Ejecutar tests según las opciones
    if args.report:
        success = generate_test_report()
    elif args.ci:
        success = run_continuous_integration()
    elif args.smoke:
        success = run_smoke_tests()
    elif args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.performance:
        success = run_performance_tests(args.verbose)
    elif args.security:
        success = run_security_tests(args.verbose)
    elif args.file:
        success = run_specific_test(args.file, args.verbose)
    elif args.all:
        success = run_all_tests(args.verbose, args.coverage, args.parallel)
    else:
        # Por defecto, ejecutar smoke tests
        print_colored("No se especificó tipo de test. Ejecutando smoke tests...", Colors.YELLOW)
        success = run_smoke_tests()
    
    # Resumen final
    end_time = time.time()
    total_duration = end_time - start_time
    
    print_colored("\n" + "=" * 80, Colors.CYAN)
    print_colored("📊 RESUMEN DE EJECUCIÓN", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 80, Colors.CYAN)
    
    print_colored(f"⏱️  Duración total: {total_duration:.2f} segundos", Colors.CYAN)
    print_colored(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.CYAN)
    
    if success:
        print_colored("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE", Colors.GREEN + Colors.BOLD)
        sys.exit(0)
    else:
        print_colored("❌ ALGUNOS TESTS FALLARON", Colors.RED + Colors.BOLD)
        sys.exit(1)

if __name__ == '__main__':
    main()
