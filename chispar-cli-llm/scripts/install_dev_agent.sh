#!/bin/bash

# Script de instalación para Chispart Dev Agent
# Versión 2.1.0 - Sistema completo con perfiles de desarrollo

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
VENV_DIR="$INSTALL_DIR/venv"

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
║    🚀 CHISPART DEV AGENT - INSTALADOR AVANZADO                              ║
║                                                                              ║
║    ✨ Asistente IA para Desarrollo con Perfiles Especializados              ║
║    🔧 Sistema de Split Chat y Seguridad Avanzada                            ║
║    🤖 60+ Modelos de IA Potentes                                             ║
║                                                                              ║
║    Versión: 2.1.0                                                           ║
║    Desarrollado por: Sebastian Vernis Mora                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"
}

detect_environment() {
    print_color $BLUE "🔍 Detectando entorno de instalación..."
    
    # Detectar Termux
    if [[ -n "$TERMUX_VERSION" ]] || [[ "$PREFIX" == *"com.termux"* ]]; then
        IS_TERMUX=true
        print_color $GREEN "📱 Entorno Termux detectado"
    else
        print_color $GREEN "💻 Entorno Linux/Unix estándar detectado"
    fi
    
    # Detectar Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_color $GREEN "✅ Python3 encontrado: $(python3 --version)"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        print_color $GREEN "✅ Python encontrado: $(python --version)"
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
    
    print_color $GREEN "✅ Comandos detectados: $PYTHON_CMD, $PIP_CMD"
}

check_system_dependencies() {
    print_color $BLUE "🔧 Verificando dependencias del sistema..."
    
    local missing_deps=()
    
    if $IS_TERMUX; then
        # Dependencias específicas de Termux
        local termux_deps=("git" "curl" "wget")
        
        for dep in "${termux_deps[@]}"; do
            if ! command -v "$dep" &> /dev/null; then
                missing_deps+=("$dep")
            fi
        done
        
        if [ ${#missing_deps[@]} -gt 0 ]; then
            print_color $YELLOW "📦 Instalando dependencias de Termux..."
            pkg update -y
            for dep in "${missing_deps[@]}"; do
                print_color $CYAN "   Instalando $dep..."
                pkg install -y "$dep"
            done
        fi
        
        # Verificar acceso al almacenamiento
        if [ ! -d "$HOME/storage" ]; then
            print_color $YELLOW "📁 Configurando acceso al almacenamiento..."
            termux-setup-storage
        fi
        
    else
        # Dependencias para sistemas Linux estándar
        local linux_deps=("git" "curl" "wget")
        
        for dep in "${linux_deps[@]}"; do
            if ! command -v "$dep" &> /dev/null; then
                missing_deps+=("$dep")
            fi
        done
        
        if [ ${#missing_deps[@]} -gt 0 ]; then
            print_color $YELLOW "⚠️  Dependencias faltantes: ${missing_deps[*]}"
            print_color $YELLOW "   Instálalas manualmente o ejecuta como root para instalación automática"
            
            if [[ $EUID -eq 0 ]]; then
                if command -v apt-get &> /dev/null; then
                    apt-get update
                    apt-get install -y "${missing_deps[@]}"
                elif command -v yum &> /dev/null; then
                    yum install -y "${missing_deps[@]}"
                elif command -v pacman &> /dev/null; then
                    pacman -S --noconfirm "${missing_deps[@]}"
                fi
            fi
        fi
    fi
    
    print_color $GREEN "✅ Dependencias del sistema verificadas"
}

create_virtual_environment() {
    print_color $BLUE "🐍 Configurando entorno virtual de Python..."
    
    if [ -d "$VENV_DIR" ]; then
        print_color $YELLOW "📁 Entorno virtual existente encontrado, recreando..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Actualizar pip
    pip install --upgrade pip
    
    print_color $GREEN "✅ Entorno virtual creado y activado"
}

install_python_dependencies() {
    print_color $BLUE "📦 Instalando dependencias de Python..."
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Dependencias principales
    local main_deps=(
        "click>=8.0.0"
        "rich>=13.0.0"
        "requests>=2.28.0"
        "python-dotenv>=0.19.0"
        "flask>=2.0.0"
        "psutil>=5.9.0"
    )
    
    # Dependencias opcionales (pueden fallar en algunos entornos)
    local optional_deps=(
        "Pillow>=9.0.0"
        "PyMuPDF>=1.20.0"
        "pypdf>=3.0.0"
    )
    
    # Instalar dependencias principales
    for dep in "${main_deps[@]}"; do
        print_color $CYAN "   Instalando $dep..."
        pip install "$dep"
    done
    
    # Instalar dependencias opcionales
    for dep in "${optional_deps[@]}"; do
        print_color $CYAN "   Instalando $dep (opcional)..."
        if ! pip install "$dep" 2>/dev/null; then
            print_color $YELLOW "   ⚠️  $dep falló, continuando sin esta funcionalidad"
        fi
    done
    
    print_color $GREEN "✅ Dependencias de Python instaladas"
}

setup_configuration() {
    print_color $BLUE "⚙️  Configurando Chispart Dev Agent..."
    
    # Crear archivo .env si no existe
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        print_color $CYAN "📝 Creando archivo de configuración..."
        cat > "$INSTALL_DIR/.env" << EOF
# Configuración de Chispart Dev Agent
# Añade tu clave de API de BlackboxAI aquí
BLACKBOX_API_KEY=your_api_key_here

# Configuración opcional
CHISPART_THEME=neon
CHISPART_DEFAULT_PROFILE=fullstack
CHISPART_SECURITY_ENABLED=true
EOF
        print_color $YELLOW "📝 Archivo .env creado. Recuerda configurar tu BLACKBOX_API_KEY"
    fi
    
    # Crear directorios necesarios
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/sessions"
    mkdir -p "$INSTALL_DIR/cache"
    
    print_color $GREEN "✅ Configuración inicial completada"
}

create_execution_scripts() {
    print_color $BLUE "🔧 Creando scripts de ejecución..."
    
    # Script principal
    cat > "$INSTALL_DIR/chispart-dev" << EOF
#!/bin/bash
# Chispart Dev Agent - Script de ejecución principal

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
cd "\$SCRIPT_DIR"

# Activar entorno virtual si existe
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Ejecutar aplicación
python chispart_dev_agent.py "\$@"
EOF
    
    # Script para interfaz web
    cat > "$INSTALL_DIR/chispart-web" << EOF
#!/bin/bash
# Chispart Dev Agent - Interfaz Web

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
cd "\$SCRIPT_DIR"

# Activar entorno virtual si existe
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "🌐 Iniciando interfaz web de Chispart Dev Agent..."
echo "📱 Accede en: http://localhost:5000"

# Ejecutar servidor web
python app.py
EOF
    
    # Script de configuración rápida
    cat > "$INSTALL_DIR/chispart-setup" << EOF
#!/bin/bash
# Chispart Dev Agent - Configuración rápida

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
cd "\$SCRIPT_DIR"

echo "🚀 Configuración rápida de Chispart Dev Agent"
echo ""

# Solicitar API key
read -p "🔑 Introduce tu clave de API de BlackboxAI: " api_key

if [ ! -z "\$api_key" ]; then
    # Actualizar archivo .env
    if [ -f ".env" ]; then
        sed -i "s/BLACKBOX_API_KEY=.*/BLACKBOX_API_KEY=\$api_key/" .env
    else
        echo "BLACKBOX_API_KEY=\$api_key" > .env
    fi
    echo "✅ Clave API configurada correctamente"
else
    echo "❌ No se proporcionó clave API"
    exit 1
fi

# Configurar perfil por defecto
echo ""
echo "👥 Selecciona tu perfil de desarrollo por defecto:"
echo "1) DevOps Engineer"
echo "2) Frontend Developer" 
echo "3) Backend Developer"
echo "4) Full Stack Developer"
echo "5) Coding Educator"
echo "6) QA Engineer"
echo "7) Project Leader"

read -p "Selecciona (1-7): " profile_choice

case \$profile_choice in
    1) profile="devops" ;;
    2) profile="frontend" ;;
    3) profile="backend" ;;
    4) profile="fullstack" ;;
    5) profile="educator" ;;
    6) profile="qa" ;;
    7) profile="project_leader" ;;
    *) profile="fullstack" ;;
esac

echo "CHISPART_DEFAULT_PROFILE=\$profile" >> .env
echo "✅ Perfil por defecto configurado: \$profile"

echo ""
echo "🎉 ¡Configuración completada!"
echo "💡 Ejecuta './chispart-dev --help' para comenzar"
EOF
    
    # Hacer scripts ejecutables
    chmod +x "$INSTALL_DIR/chispart-dev"
    chmod +x "$INSTALL_DIR/chispart-web"
    chmod +x "$INSTALL_DIR/chispart-setup"
    
    print_color $GREEN "✅ Scripts de ejecución creados"
}

setup_global_access() {
    print_color $BLUE "🌐 Configurando acceso global (opcional)..."
    
    local bin_dir=""
    
    if $IS_TERMUX; then
        bin_dir="$PREFIX/bin"
    else
        # Buscar directorio bin apropiado
        if [ -d "$HOME/.local/bin" ]; then
            bin_dir="$HOME/.local/bin"
        elif [ -d "$HOME/bin" ]; then
            bin_dir="$HOME/bin"
        else
            mkdir -p "$HOME/.local/bin"
            bin_dir="$HOME/.local/bin"
        fi
    fi
    
    if [ -w "$bin_dir" ]; then
        print_color $CYAN "📁 Creando enlaces simbólicos en $bin_dir..."
        
        # Crear enlaces simbólicos
        ln -sf "$INSTALL_DIR/chispart-dev" "$bin_dir/chispart-dev"
        ln -sf "$INSTALL_DIR/chispart-web" "$bin_dir/chispart-web"
        ln -sf "$INSTALL_DIR/chispart-setup" "$bin_dir/chispart-setup"
        
        # Crear alias cortos
        ln -sf "$INSTALL_DIR/chispart-dev" "$bin_dir/cdev"
        ln -sf "$INSTALL_DIR/chispart-web" "$bin_dir/cweb"
        
        print_color $GREEN "✅ Acceso global configurado"
        print_color $CYAN "💡 Ahora puedes usar: chispart-dev, cdev, chispart-web, cweb"
        
        # Verificar PATH
        if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
            print_color $YELLOW "⚠️  Añade $bin_dir a tu PATH para acceso global"
            print_color $CYAN "   Ejecuta: echo 'export PATH=\"$bin_dir:\$PATH\"' >> ~/.bashrc"
        fi
    else
        print_color $YELLOW "⚠️  No se pudo configurar acceso global (permisos insuficientes)"
        print_color $CYAN "💡 Usa los scripts locales: ./chispart-dev, ./chispart-web"
    fi
}

verify_installation() {
    print_color $BLUE "🧪 Verificando instalación..."
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Verificar que el script principal funciona
    if $PYTHON_CMD chispart_dev_agent.py --help &> /dev/null; then
        print_color $GREEN "✅ CLI principal funciona correctamente"
    else
        print_color $RED "❌ Error en CLI principal"
        return 1
    fi
    
    # Verificar importaciones críticas
    if $PYTHON_CMD -c "
import sys
sys.path.append('.')
try:
    from core.dev_profiles import profile_manager
    from core.split_chat_manager import split_chat_manager
    from core.security_manager import security_manager
    from config_extended import get_available_models
    print('✅ Todos los módulos importados correctamente')
except ImportError as e:
    print(f'❌ Error importando módulos: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_color $GREEN "✅ Módulos principales verificados"
    else
        print_color $RED "❌ Error en módulos principales"
        return 1
    fi
    
    # Verificar modelos disponibles
    local model_count=$($PYTHON_CMD -c "
import sys
sys.path.append('.')
from config_extended import get_available_models
models = get_available_models('chispart')
print(len(models))
" 2>/dev/null)
    
    if [ "$model_count" -gt 50 ]; then
        print_color $GREEN "✅ $model_count modelos de IA disponibles"
    else
        print_color $YELLOW "⚠️  Solo $model_count modelos disponibles (esperados 60+)"
    fi
    
    print_color $GREEN "✅ Instalación verificada correctamente"
    return 0
}

show_post_install_info() {
    print_color $GREEN "
🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!

╔══════════════════════════════════════════════════════════════════════════════╗
║                        CHISPART DEV AGENT v2.1.0                            ║
║                     ¡Listo para usar como agente de desarrollo!             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"

    print_color $CYAN "
🚀 PRIMEROS PASOS:

1️⃣  Configurar API Key:
   ./chispart-setup

2️⃣  Probar la instalación:
   ./chispart-dev --help
   ./chispart-dev version

3️⃣  Seleccionar perfil de desarrollo:
   ./chispart-dev perfiles

4️⃣  Primer chat con IA:
   ./chispart-dev chat \"Hola, soy un desarrollador\" --profile fullstack
"

    print_color $BLUE "
🔧 COMANDOS PRINCIPALES:

💬 Chat con perfiles especializados:
   ./chispart-dev chat \"Crea una API REST\" --profile backend
   ./chispart-dev chat \"Diseña un componente React\" --profile frontend

🔀 Sistema de Split Chat:
   ./chispart-dev split-chat \"Team Frontend\" --profile frontend
   ./chispart-dev split-list
   ./chispart-dev merge-chat session1 session2

⚡ Ejecución segura de comandos:
   ./chispart-dev execute \"git status\" --safe
   ./chispart-dev security

🤖 Gestión de modelos:
   ./chispart-dev modelos
"

    print_color $YELLOW "
🌐 INTERFAZ WEB:
   ./chispart-web                 - Lanzar interfaz web
   http://localhost:5000          - Acceder desde navegador
"

    print_color $PURPLE "
👥 PERFILES DE DESARROLLO DISPONIBLES:
   • DevOps Engineer      - Infraestructura y CI/CD
   • Frontend Developer   - Interfaces de usuario
   • Backend Developer    - APIs y servicios
   • Full Stack Developer - Desarrollo completo
   • Coding Educator      - Enseñanza de programación
   • QA Engineer          - Testing y calidad
   • Project Leader       - Gestión técnica de proyectos
"

    print_color $GREEN "
✨ CARACTERÍSTICAS AVANZADAS:
   • 60+ modelos de IA potentes (GPT-4, Claude, Llama, Gemini, etc.)
   • Sistema de seguridad con whitelist de comandos
   • Split chat para equipos de desarrollo
   • Perfiles especializados por rol
   • Interfaz moderna optimizada para desarrollo
   • Ejecución segura de comandos del sistema
"

    print_color $CYAN "
📚 DOCUMENTACIÓN:
   • README.md              - Guía completa
   • EQUIPOS_DESARROLLO.md   - Plan de desarrollo en equipos
   • ./chispart-dev --help   - Ayuda de comandos
"

    print_color $GREEN "
🎯 ¡CHISPART DEV AGENT ESTÁ LISTO!
   Tu asistente IA especializado para desarrollo ya está configurado.
   ¡Comienza a desarrollar con la potencia de la IA!
"
}

# Función principal
main() {
    print_banner
    
    # Paso 1: Detectar entorno
    detect_environment
    
    # Paso 2: Verificar dependencias del sistema
    check_system_dependencies
    
    # Paso 3: Crear entorno virtual
    create_virtual_environment
    
    # Paso 4: Instalar dependencias Python
    install_python_dependencies
    
    # Paso 5: Configurar aplicación
    setup_configuration
    
    # Paso 6: Crear scripts de ejecución
    create_execution_scripts
    
    # Paso 7: Configurar acceso global (opcional)
    setup_global_access
    
    # Paso 8: Verificar instalación
    if verify_installation; then
        # Paso 9: Mostrar información post-instalación
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
