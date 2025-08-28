#!/bin/bash

# ============================================================================
# CHISPART CLI - INSTALADOR MEJORADO CON PLAYGROUND INTERACTIVO
# ============================================================================
# Este script instala Chispart CLI y lanza automáticamente el playground
# interactivo para que los usuarios aprendan todos los comandos.
# ============================================================================

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Banner de bienvenida
show_banner() {
    clear
    print_colored $CYAN "╔══════════════════════════════════════════════════════════════════╗"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "║  $(print_colored $WHITE "🚀 CHISPART CLI - INSTALADOR MEJORADO")                        ║"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "║  $(print_colored $YELLOW "✨ Instalación automática + Playground interactivo")            ║"
    print_colored $CYAN "║  $(print_colored $BLUE "🎮 Aprende todos los comandos paso a paso")                   ║"
    print_colored $CYAN "║  $(print_colored $GREEN "🛡️ Sistema de seguridad integrado")                           ║"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "╚══════════════════════════════════════════════════════════════════╝"
    echo
}

# Verificar prerequisitos
check_prerequisites() {
    print_colored $BLUE "🔍 Verificando prerequisitos del sistema..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        print_colored $RED "❌ Python 3 no está instalado"
        print_colored $YELLOW "💡 Instala Python 3.8+ antes de continuar"
        exit 1
    fi
    
    # Verificar versión de Python
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.8"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_colored $RED "❌ Python $python_version detectado. Se requiere Python $required_version+"
        exit 1
    fi
    
    print_colored $GREEN "✅ Python $python_version detectado"
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_colored $RED "❌ pip no está instalado"
        print_colored $YELLOW "💡 Instala pip antes de continuar"
        exit 1
    fi
    
    print_colored $GREEN "✅ pip disponible"
    
    # Verificar git (opcional pero recomendado)
    if command -v git &> /dev/null; then
        print_colored $GREEN "✅ Git disponible"
    else
        print_colored $YELLOW "⚠️  Git no disponible (opcional)"
    fi
    
    # Detectar entorno (Termux vs Desktop)
    if [[ -n "$TERMUX_VERSION" ]]; then
        ENVIRONMENT="termux"
        print_colored $PURPLE "📱 Entorno Termux detectado"
    else
        ENVIRONMENT="desktop"
        print_colored $BLUE "🖥️  Entorno Desktop detectado"
    fi
    
    print_colored $GREEN "✅ Prerequisitos verificados"
    echo
}

# Instalar dependencias
install_dependencies() {
    print_colored $BLUE "📦 Instalando dependencias de Python..."
    
    # Crear entorno virtual si no existe
    if [[ ! -d "venv" ]]; then
        print_colored $YELLOW "🔧 Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Actualizar pip
    print_colored $YELLOW "🔄 Actualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependencias principales
    print_colored $YELLOW "📚 Instalando dependencias principales..."
    pip install -r requirements.txt
    
    # Instalar dependencias adicionales para el playground
    print_colored $YELLOW "🎮 Instalando dependencias del playground..."
    pip install rich>=13.0.0 prompt-toolkit>=3.0.0
    
    # Dependencias específicas para Termux
    if [[ "$ENVIRONMENT" == "termux" ]]; then
        print_colored $PURPLE "📱 Instalando optimizaciones para Termux..."
        pip install psutil memory-profiler
    fi
    
    print_colored $GREEN "✅ Dependencias instaladas correctamente"
    echo
}

# Configurar permisos y scripts
setup_scripts() {
    print_colored $BLUE "🔧 Configurando scripts ejecutables..."
    
    # Hacer ejecutables los scripts principales
    chmod +x chispart
    chmod +x chs
    chmod +x chispart_dev_agent_v3.py
    
    # Crear enlaces simbólicos si no existen
    if [[ ! -L "/usr/local/bin/chispart" ]] && [[ "$ENVIRONMENT" == "desktop" ]]; then
        if [[ -w "/usr/local/bin" ]]; then
            ln -sf "$(pwd)/chispart" /usr/local/bin/chispart
            print_colored $GREEN "✅ Enlace simbólico creado en /usr/local/bin"
        else
            print_colored $YELLOW "⚠️  No se pudo crear enlace simbólico (permisos insuficientes)"
            print_colored $BLUE "💡 Puedes usar ./chispart desde este directorio"
        fi
    fi
    
    print_colored $GREEN "✅ Scripts configurados"
    echo
}

# Configuración inicial interactiva
interactive_setup() {
    print_colored $BLUE "⚙️ Configuración inicial interactiva..."
    echo
    
    # Preguntar si quiere configurar APIs ahora
    read -p "$(print_colored $CYAN "¿Deseas configurar las APIs de IA ahora? (s/N): ")" configure_apis
    
    if [[ "$configure_apis" =~ ^[Ss]$ ]]; then
        print_colored $YELLOW "🔑 Configurando APIs..."
        
        # Configurar API principal (Chispart/BlackboxAI)
        echo
        print_colored $BLUE "📋 API Principal: Chispart (BlackboxAI)"
        print_colored $YELLOW "💡 Obtén tu API key en: https://www.blackbox.ai/api"
        read -p "$(print_colored $CYAN "Ingresa tu Chispart API Key (opcional): ")" chispart_key
        
        if [[ -n "$chispart_key" ]]; then
            echo "export CHISPART_API_KEY=\"$chispart_key\"" >> ~/.bashrc
            echo "export BLACKBOX_API_KEY=\"$chispart_key\"" >> ~/.bashrc
            print_colored $GREEN "✅ Chispart API configurada"
        fi
        
        # Configurar APIs adicionales (opcional)
        echo
        print_colored $BLUE "📋 APIs Adicionales (Opcional)"
        
        # Qwen AI
        read -p "$(print_colored $CYAN "¿Configurar Qwen AI? (s/N): ")" setup_qwen
        if [[ "$setup_qwen" =~ ^[Ss]$ ]]; then
            print_colored $YELLOW "💡 Obtén tu API key en: https://dashscope.aliyun.com"
            read -p "$(print_colored $CYAN "Qwen API Key: ")" qwen_key
            if [[ -n "$qwen_key" ]]; then
                echo "export QWEN_API_KEY=\"$qwen_key\"" >> ~/.bashrc
                print_colored $GREEN "✅ Qwen AI configurada"
            fi
        fi
        
        # Google Gemini
        read -p "$(print_colored $CYAN "¿Configurar Google Gemini? (s/N): ")" setup_gemini
        if [[ "$setup_gemini" =~ ^[Ss]$ ]]; then
            print_colored $YELLOW "💡 Obtén tu API key en: https://makersuite.google.com/app/apikey"
            read -p "$(print_colored $CYAN "Gemini API Key: ")" gemini_key
            if [[ -n "$gemini_key" ]]; then
                echo "export GEMINI_API_KEY=\"$gemini_key\"" >> ~/.bashrc
                print_colored $GREEN "✅ Google Gemini configurada"
            fi
        fi
        
        # Recargar bashrc
        source ~/.bashrc 2>/dev/null || true
        
    else
        print_colored $YELLOW "⏭️  Configuración de APIs omitida"
        print_colored $BLUE "💡 Puedes configurarlas después con: ./chispart config"
    fi
    
    echo
}

# Verificar instalación
verify_installation() {
    print_colored $BLUE "🧪 Verificando instalación..."
    
    # Verificar que el script principal funciona
    if ./chispart version &>/dev/null; then
        print_colored $GREEN "✅ Chispart CLI funciona correctamente"
    else
        print_colored $YELLOW "⚠️  Chispart CLI instalado pero puede necesitar configuración"
    fi
    
    # Verificar dependencias críticas
    python3 -c "import rich, requests, json" 2>/dev/null
    if [[ $? -eq 0 ]]; then
        print_colored $GREEN "✅ Dependencias críticas verificadas"
    else
        print_colored $RED "❌ Algunas dependencias faltan"
        return 1
    fi
    
    # Verificar playground
    if [[ -f "ui/interactive_playground.py" ]]; then
        print_colored $GREEN "✅ Playground interactivo disponible"
    else
        print_colored $YELLOW "⚠️  Playground no encontrado"
    fi
    
    print_colored $GREEN "✅ Instalación verificada"
    echo
}

# Lanzar playground interactivo
launch_playground() {
    print_colored $BLUE "🎮 ¿Deseas iniciar el playground interactivo para aprender Chispart CLI?"
    print_colored $YELLOW "💡 El playground te enseñará todos los comandos paso a paso"
    echo
    
    read -p "$(print_colored $CYAN "¿Iniciar playground ahora? (S/n): ")" start_playground
    
    if [[ ! "$start_playground" =~ ^[Nn]$ ]]; then
        print_colored $GREEN "🚀 Iniciando playground interactivo..."
        echo
        
        # Activar entorno virtual si existe
        if [[ -d "venv" ]]; then
            source venv/bin/activate
        fi
        
        # Lanzar playground
        python3 ui/interactive_playground.py
    else
        print_colored $BLUE "💡 Puedes iniciar el playground después con:"
        print_colored $WHITE "   python3 ui/interactive_playground.py"
        print_colored $WHITE "   # o"
        print_colored $WHITE "   ./chispart playground"
    fi
}

# Mostrar resumen final
show_summary() {
    echo
    print_colored $CYAN "╔══════════════════════════════════════════════════════════════════╗"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "║  $(print_colored $GREEN "🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")                     ║"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "║  $(print_colored $WHITE "Comandos principales:")                                        ║"
    print_colored $CYAN "║  $(print_colored $YELLOW "• ./chispart chat \"Hola mundo\"")                             ║"
    print_colored $CYAN "║  $(print_colored $YELLOW "• ./chispart perfiles")                                       ║"
    print_colored $CYAN "║  $(print_colored $YELLOW "• ./chispart analizar-directorio .")                          ║"
    print_colored $CYAN "║  $(print_colored $YELLOW "• ./chispart playground")                                     ║"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "║  $(print_colored $WHITE "Recursos útiles:")                                            ║"
    print_colored $CYAN "║  $(print_colored $BLUE "• ./chispart ayuda - Ayuda completa")                        ║"
    print_colored $CYAN "║  $(print_colored $BLUE "• ./chispart config - Configurar APIs")                      ║"
    print_colored $CYAN "║  $(print_colored $BLUE "• ./chispart version - Info del sistema")                    ║"
    print_colored $CYAN "║                                                                  ║"
    print_colored $CYAN "╚══════════════════════════════════════════════════════════════════╝"
    echo
    
    print_colored $GREEN "🚀 ¡Chispart CLI está listo para usar!"
    print_colored $BLUE "💡 Recuerda: El playground interactivo te ayudará a dominar todos los comandos"
    echo
}

# Función principal
main() {
    # Verificar si se ejecuta con --interactive
    INTERACTIVE_MODE=false
    if [[ "$1" == "--interactive" ]]; then
        INTERACTIVE_MODE=true
    fi
    
    show_banner
    
    # Verificar si ya estamos en el directorio correcto
    if [[ ! -f "chispart_dev_agent_v3.py" ]]; then
        print_colored $RED "❌ Error: Ejecuta este script desde el directorio de Chispart CLI"
        print_colored $BLUE "💡 cd chispar-cli-llm && ./install-enhanced.sh"
        exit 1
    fi
    
    # Ejecutar pasos de instalación
    check_prerequisites
    install_dependencies
    setup_scripts
    
    if [[ "$INTERACTIVE_MODE" == "true" ]]; then
        interactive_setup
    fi
    
    verify_installation
    
    # Siempre ofrecer el playground
    launch_playground
    
    show_summary
    
    print_colored $PURPLE "🎯 ¡Disfruta desarrollando con IA!"
}

# Manejo de errores
trap 'print_colored $RED "❌ Error durante la instalación. Revisa los logs arriba."; exit 1' ERR

# Ejecutar función principal
main "$@"
