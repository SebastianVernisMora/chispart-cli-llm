#!/bin/bash

# =============================================================================
# 🚀 Chispart Dev Agent v3.0 - Script de Instalación Principal
# =============================================================================
# Instalador universal para Chispart Dev Agent
# Soporta: Linux, macOS, Termux (Android)
# =============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$SCRIPT_DIR"
PYTHON_CMD=""
PIP_CMD=""
IS_TERMUX=false

# =============================================================================
# Funciones de utilidad
# =============================================================================

print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_banner() {
    clear
    print_color $CYAN "
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🚀 CHISPART DEV AGENT v3.0 - INSTALACIÓN                                 ║
║                                                                              ║
║    ✨ Agente de Desarrollo con IA Híbrida                                    ║
║    🤖 100+ Modelos de IA Disponibles                                         ║
║    👥 Gestión de Equipos de Desarrollo                                       ║
║    🆘 Asistencia Técnica ATC                                                 ║
║    ⚡ Ejecución Segura de Comandos                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"
}

detect_environment() {
    print_color $BLUE "🔍 Detectando entorno de instalación..."
    
    # Detectar Termux
    if [[ -n "$TERMUX_VERSION" ]] || [[ "$PREFIX" == *"com.termux"* ]]; then
        IS_TERMUX=true
        print_color $GREEN "✅ Entorno detectado: Termux (Android)"
    else
        print_color $GREEN "✅ Entorno detectado: Sistema estándar (Linux/macOS)"
    fi
    
    # Detectar Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_color $RED "❌ Python no encontrado"
        exit 1
    fi
    
    # Detectar pip
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_color $RED "❌ pip no encontrado"
        exit 1
    fi
    
    print_color $GREEN "✅ Python: $PYTHON_CMD"
    print_color $GREEN "✅ pip: $PIP_CMD"
}

check_system_dependencies() {
    print_color $BLUE "🔧 Verificando dependencias del sistema..."
    
    if $IS_TERMUX; then
        # Dependencias específicas de Termux
        local termux_deps=("git" "curl" "wget")
        for dep in "${termux_deps[@]}"; do
            if ! command -v "$dep" &> /dev/null; then
                print_color $YELLOW "⚠️  Instalando $dep..."
                pkg install -y "$dep"
            else
                print_color $GREEN "✅ $dep disponible"
            fi
        done
    else
        # Verificar dependencias estándar
        local deps=("git" "curl")
        for dep in "${deps[@]}"; do
            if ! command -v "$dep" &> /dev/null; then
                print_color $YELLOW "⚠️  $dep no encontrado. Por favor instálalo manualmente."
            else
                print_color $GREEN "✅ $dep disponible"
            fi
        done
    fi
}

install_python_dependencies() {
    print_color $BLUE "📦 Instalando dependencias de Python..."
    
    # Crear requirements.txt si no existe
    if [[ ! -f "$INSTALL_DIR/requirements.txt" ]]; then
        cat > "$INSTALL_DIR/requirements.txt" << EOF
click>=8.0.0
rich>=13.0.0
requests>=2.28.0
python-dotenv>=0.19.0
flask>=2.0.0
pillow>=9.0.0
PyMuPDF>=1.20.0
pypdf>=3.0.0
cryptography>=3.4.0
pyyaml>=6.0
EOF
    fi
    
    # Instalar dependencias
    if $IS_TERMUX; then
        # Instalación optimizada para Termux
        print_color $YELLOW "📱 Instalando para Termux..."
        $PIP_CMD install --upgrade pip
        $PIP_CMD install -r "$INSTALL_DIR/requirements.txt" --no-cache-dir
    else
        # Instalación estándar
        $PIP_CMD install --upgrade pip
        $PIP_CMD install -r "$INSTALL_DIR/requirements.txt"
    fi
    
    print_color $GREEN "✅ Dependencias de Python instaladas"
}

create_execution_scripts() {
    print_color $BLUE "📝 Creando scripts de ejecución..."
    
    # Script principal chispart
    cat > "$INSTALL_DIR/chispart" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 chispart_dev_agent_v3.py "$@"
EOF
    chmod +x "$INSTALL_DIR/chispart"
    
    # Script corto chs
    cat > "$INSTALL_DIR/chs" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 chispart_dev_agent_v3.py "$@"
EOF
    chmod +x "$INSTALL_DIR/chs"
    
    print_color $GREEN "✅ Scripts de ejecución creados"
}

setup_global_access() {
    print_color $BLUE "🌐 Configurando acceso global (opcional)..."
    
    local shell_rc=""
    if [[ -n "$BASH_VERSION" ]]; then
        shell_rc="$HOME/.bashrc"
    elif [[ -n "$ZSH_VERSION" ]]; then
        shell_rc="$HOME/.zshrc"
    fi
    
    if [[ -n "$shell_rc" ]] && [[ -f "$shell_rc" ]]; then
        # Agregar al PATH si no está ya
        if ! grep -q "export PATH.*$INSTALL_DIR" "$shell_rc"; then
            echo "" >> "$shell_rc"
            echo "# Chispart Dev Agent" >> "$shell_rc"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$shell_rc"
            print_color $GREEN "✅ Agregado al PATH en $shell_rc"
            print_color $YELLOW "⚠️  Ejecuta 'source $shell_rc' o reinicia tu terminal"
        else
            print_color $GREEN "✅ Ya está en el PATH"
        fi
    fi
}

verify_installation() {
    print_color $BLUE "🔍 Verificando instalación..."
    
    # Verificar que el script principal existe
    if [[ ! -f "$INSTALL_DIR/chispart_dev_agent_v3.py" ]]; then
        print_color $RED "❌ Archivo principal no encontrado"
        return 1
    fi
    
    # Verificar que los scripts de ejecución funcionan
    if ! "$INSTALL_DIR/chispart" --help &> /dev/null; then
        print_color $RED "❌ Script chispart no funciona"
        return 1
    fi
    
    print_color $GREEN "✅ Instalación verificada correctamente"
    return 0
}

show_post_install_info() {
    print_color $GREEN "
🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!

📋 Comandos disponibles:
   ./chispart --help             - Ayuda completa
   ./chs --help                  - Ayuda completa (versión corta)
   
🤖 Comandos principales:
   ./chispart chat \"Hola IA\"      - Chat con IA
   ./chispart execute \"pwd\"       - Ejecutar comando seguro
   ./chispart equipos             - Gestionar equipos
   ./chispart atc                 - Asistencia técnica
   ./chispart modelos             - Ver modelos disponibles
   
⚙️ Configuración:
   ./chispart config              - Configurar APIs
   
📚 Documentación completa:
   ./chispart ayuda               - Guía completa
   docs/CHISPART_DEV_AGENT_V3_COMPLETADO.md
"

    if $IS_TERMUX; then
        print_color $CYAN "
📱 Optimizaciones para Termux activadas:
   - Timeouts optimizados para móviles
   - Paths seguros para Android
   - Configuración de red adaptativa
"
    fi

    print_color $YELLOW "
🔑 Próximos pasos:
   1. Configura tus APIs: ./chispart config
   2. Prueba el chat: ./chispart chat \"¡Hola!\"
   3. Explora la ayuda: ./chispart ayuda
"
}

# =============================================================================
# Función principal
# =============================================================================

main() {
    print_banner
    
    # Paso 1: Detectar entorno
    detect_environment
    
    # Paso 2: Verificar dependencias del sistema
    check_system_dependencies
    
    # Paso 3: Instalar dependencias Python
    install_python_dependencies
    
    # Paso 4: Crear scripts de ejecución
    create_execution_scripts
    
    # Paso 5: Configurar acceso global (opcional)
    setup_global_access
    
    # Paso 6: Verificar instalación
    if verify_installation; then
        # Paso 7: Mostrar información post-instalación
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
