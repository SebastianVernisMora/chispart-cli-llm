#!/bin/bash

# Chispart CLI Modern - Script de Instalación
# Instala la versión modernizada con arquitectura modular

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Banner de instalación
print_banner() {
    print_color $CYAN "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚀 CHISPART CLI MODERN - INSTALACIÓN AUTOMATIZADA        ║
║                                                              ║
║    Interfaz Universal para LLMs con Arquitectura Modular    ║
║    Optimizado para Termux/Android y Sistemas Unix           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"
}

# Detectar entorno
detect_environment() {
    print_color $BLUE "🔍 Detectando entorno de instalación..."
    
    if [[ -n "$TERMUX_VERSION" ]]; then
        ENVIRONMENT="termux"
        print_color $GREEN "✅ Entorno Termux detectado"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        ENVIRONMENT="linux"
        print_color $GREEN "✅ Entorno Linux detectado"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        ENVIRONMENT="macos"
        print_color $GREEN "✅ Entorno macOS detectado"
    else
        ENVIRONMENT="unknown"
        print_color $YELLOW "⚠️ Entorno no reconocido, usando configuración genérica"
    fi
}

# Verificar dependencias del sistema
check_system_dependencies() {
    print_color $BLUE "🔧 Verificando dependencias del sistema..."
    
    local missing_deps=()
    
    # Python 3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # pip
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    # git (opcional pero recomendado)
    if ! command -v git &> /dev/null; then
        print_color $YELLOW "⚠️ Git no encontrado (opcional para actualizaciones)"
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_color $RED "❌ Dependencias faltantes: ${missing_deps[*]}"
        
        if [[ "$ENVIRONMENT" == "termux" ]]; then
            print_color $CYAN "📱 Para instalar en Termux:"
            print_color $CYAN "   pkg update && pkg install python git"
        elif [[ "$ENVIRONMENT" == "linux" ]]; then
            print_color $CYAN "🐧 Para instalar en Linux:"
            print_color $CYAN "   sudo apt update && sudo apt install python3 python3-pip git"
        elif [[ "$ENVIRONMENT" == "macos" ]]; then
            print_color $CYAN "🍎 Para instalar en macOS:"
            print_color $CYAN "   brew install python3 git"
        fi
        
        exit 1
    fi
    
    print_color $GREEN "✅ Dependencias del sistema verificadas"
}

# Instalar dependencias Python
install_python_dependencies() {
    print_color $BLUE "📦 Instalando dependencias Python..."
    
    # Crear requirements.txt si no existe
    if [[ ! -f "requirements.txt" ]]; then
        print_color $YELLOW "⚠️ requirements.txt no encontrado, creando uno básico..."
        cat > requirements.txt << EOF
click>=8.0.0
rich>=13.0.0
requests>=2.28.0
python-dotenv>=0.19.0
flask>=2.0.0
pillow>=9.0.0
PyMuPDF>=1.20.0
pypdf>=3.0.0
EOF
    fi
    
    # Instalar dependencias
    if [[ "$ENVIRONMENT" == "termux" ]]; then
        # Configuración especial para Termux
        print_color $CYAN "📱 Instalando para Termux con optimizaciones..."
        
        # Instalar dependencias básicas primero
        python3 -m pip install --upgrade pip
        python3 -m pip install click rich requests python-dotenv flask
        
        # Intentar instalar Pillow (puede fallar en algunos dispositivos)
        if ! python3 -m pip install pillow; then
            print_color $YELLOW "⚠️ Pillow no se pudo instalar, análisis de imágenes limitado"
        fi
        
        # Intentar instalar PyMuPDF (puede requerir compilación)
        if ! python3 -m pip install PyMuPDF; then
            print_color $YELLOW "⚠️ PyMuPDF no se pudo instalar, intentando pypdf..."
            if ! python3 -m pip install pypdf; then
                print_color $YELLOW "⚠️ Análisis de PDF limitado"
            fi
        fi
        
    else
        # Instalación estándar
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
    fi
    
    print_color $GREEN "✅ Dependencias Python instaladas"
}

# Configurar estructura de directorios
setup_directory_structure() {
    print_color $BLUE "📁 Configurando estructura de directorios..."
    
    # Crear directorios necesarios
    mkdir -p config
    mkdir -p logs
    mkdir -p backup_legacy
    mkdir -p tests
    
    # Crear archivo de configuración inicial si no existe
    if [[ ! -f "config/chispart_config.json" ]]; then
        cat > config/chispart_config.json << EOF
{
  "version": "2.0.0",
  "configured_apis": [],
  "current_api": "chispart",
  "current_theme": "neon",
  "user_preferences": {
    "save_history": true,
    "stream_responses": false,
    "show_tokens": true,
    "auto_detect_termux": true
  },
  "installation": {
    "date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "environment": "$ENVIRONMENT",
    "version": "2.0.0"
  }
}
EOF
    fi
    
    print_color $GREEN "✅ Estructura de directorios configurada"
}

# Crear scripts de ejecución
create_execution_scripts() {
    print_color $BLUE "🔧 Creando scripts de ejecución..."
    
    local script_dir="$(pwd)"
    
    # Script principal
    cat > chispart << 'EOF'
#!/bin/bash
# Chispart CLI Modern - Script principal
cd "$(dirname "$0")"
python3 chispart_cli_modern.py "$@"
EOF
    chmod +x chispart
    
    # Alias corto
    cat > chs << 'EOF'
#!/bin/bash
# Chispart CLI Modern - Alias corto
cd "$(dirname "$0")"
python3 chispart_cli_modern.py "$@"
EOF
    chmod +x chs
    
    # Script para interfaz web (mantener compatibilidad)
    cat > chispart-ui << 'EOF'
#!/bin/bash
# Chispart CLI Modern - Interfaz Web
cd "$(dirname "$0")"
python3 app.py
EOF
    chmod +x chispart-ui
    
    # Script de migración
    cat > chispart-migrate << 'EOF'
#!/bin/bash
# Chispart CLI Modern - Migración desde legacy
cd "$(dirname "$0")"
python3 migrate_to_modern.py
EOF
    chmod +x chispart-migrate
    
    print_color $GREEN "✅ Scripts de ejecución creados"
}

# Configurar acceso global (opcional)
setup_global_access() {
    print_color $BLUE "🌐 Configurando acceso global..."
    
    local install_dir="$(pwd)"
    local bin_dir=""
    
    if [[ "$ENVIRONMENT" == "termux" ]]; then
        bin_dir="$PREFIX/bin"
    else
        bin_dir="$HOME/.local/bin"
        mkdir -p "$bin_dir"
    fi
    
    # Crear enlaces simbólicos
    if [[ -w "$bin_dir" ]]; then
        ln -sf "$install_dir/chispart" "$bin_dir/chispart" 2>/dev/null || true
        ln -sf "$install_dir/chs" "$bin_dir/chs" 2>/dev/null || true
        
        print_color $GREEN "✅ Acceso global configurado en $bin_dir"
        
        # Verificar que esté en PATH
        if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
            print_color $YELLOW "⚠️ Agrega $bin_dir a tu PATH para acceso global"
            if [[ "$ENVIRONMENT" == "termux" ]]; then
                print_color $CYAN "   echo 'export PATH=\$PATH:$bin_dir' >> ~/.bashrc"
            else
                print_color $CYAN "   echo 'export PATH=\$PATH:$bin_dir' >> ~/.bashrc"
            fi
        fi
    else
        print_color $YELLOW "⚠️ No se pudo configurar acceso global (permisos insuficientes)"
    fi
}

# Verificar instalación
verify_installation() {
    print_color $BLUE "🧪 Verificando instalación..."
    
    # Verificar que el script principal funcione
    if ./chispart version &> /dev/null; then
        print_color $GREEN "✅ Script principal funciona correctamente"
    else
        print_color $RED "❌ Error en el script principal"
        return 1
    fi
    
    # Verificar imports Python
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from core import ChispartCLIManager
    from ui.theme_manager import ThemeManager
    from ui.components import console
    print('✅ Imports verificados')
except ImportError as e:
    print(f'❌ Error de import: {e}')
    sys.exit(1)
"; then
        print_color $GREEN "✅ Módulos Python verificados"
    else
        print_color $RED "❌ Error en módulos Python"
        return 1
    fi
    
    print_color $GREEN "✅ Instalación verificada exitosamente"
}

# Mostrar información post-instalación
show_post_install_info() {
    print_color $CYAN "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"
    
    print_color $GREEN "📋 Próximos pasos:"
    print_color $CYAN "
1. Configurar APIs:
   ./chispart configurar

2. Verificar estado:
   ./chispart estado

3. Primer chat:
   ./chispart chat \"¡Hola desde Chispart CLI Modern!\"

4. Modo interactivo:
   ./chispart interactivo

5. Ver ayuda completa:
   ./chispart --help
"
    
    if [[ -f "chispart_cli.py" ]]; then
        print_color $YELLOW "
🔄 MIGRACIÓN DESDE VERSIÓN LEGACY:
Si tienes una instalación anterior de Chispart CLI, puedes migrar
tu configuración y historial:

   ./chispart-migrate
"
    fi
    
    print_color $PURPLE "
📚 Comandos útiles:
   ./chispart chat \"mensaje\"     - Chat rápido
   ./chs i                        - Modo interactivo (alias)
   ./chispart imagen foto.jpg     - Analizar imagen
   ./chispart pdf documento.pdf   - Analizar PDF
   ./chispart tema                - Cambiar tema
   ./chispart historial           - Ver historial
"
    
    print_color $BLUE "
🌐 Interfaz Web:
   ./chispart-ui                  - Lanzar interfaz web
   http://localhost:5000          - Acceder desde navegador
"
    
    print_color $GREEN "
✨ ¡Disfruta de tu nueva experiencia con Chispart CLI Modern!
"
}

# Función principal
main() {
    print_banner
    
    # Paso 1: Detectar entorno
    detect_environment
    
    # Paso 2: Verificar dependencias del sistema
    check_system_dependencies
    
    # Paso 3: Instalar dependencias Python
    install_python_dependencies
    
    # Paso 4: Configurar estructura de directorios
    setup_directory_structure
    
    # Paso 5: Crear scripts de ejecución
    create_execution_scripts
    
    # Paso 6: Configurar acceso global (opcional)
    setup_global_access
    
    # Paso 7: Verificar instalación
    if verify_installation; then
        # Paso 8: Mostrar información post-instalación
        show_post_install_info
    else
        print_color $RED "❌ La instalación falló en la verificación"
        exit 1
    fi
}

# Ejecutar función principal si el script se ejecuta directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
    
