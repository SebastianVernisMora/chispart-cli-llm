#!/bin/bash

# 🚀 Script de instalación para Chispart-CLI-LLM
# Universal LLM Terminal for Mobile Devices

set -e

echo "🚀 Instalando Chispart-CLI-LLM en Termux..."
echo "============================================="
echo ""
echo "   _____ _     _                       _   "
echo "  / ____| |   (_)                     | |  "
echo " | |    | |__  _ ___ _ __   __ _ _ __  | |_ "
echo " | |    | '_ \| / __| '_ \ / _\` | '__| | __|"
echo " | |____| | | | \__ \ |_) | (_| | |    | |_ "
echo "  \_____|_| |_|_|___/ .__/ \__,_|_|     \__|"
echo "                    | |                     "
echo "                    |_|                     "
echo "        Universal LLM Terminal for Mobile"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}[CHISPART]${NC} $1"
}

# Verificar que estamos en Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "Este script está diseñado para ejecutarse en Termux"
    exit 1
fi

print_header "Actualizando paquetes de Termux..."
pkg update -y

print_header "Instalando dependencias del sistema..."
# Instalar dependencias necesarias para Python y las librerías
pkg install -y python python-pip git libffi openssl libjpeg-turbo libpng zlib freetype

# Dependencias adicionales para PyMuPDF
pkg install -y clang make cmake

print_header "Actualizando pip..."
pip install --upgrade pip setuptools wheel

print_header "Instalando dependencias Python optimizadas para Termux..."

# Crear requirements específicos para Termux
cat > requirements_chispart.txt << 'EOF'
requests>=2.31.0
click>=8.1.0
rich>=13.0.0
python-dotenv>=1.0.0
Flask>=2.0.0
Pillow>=10.0.0

# PyMuPDF puede ser problemático, intentamos instalarlo
# Si falla, el script continuará sin él
PyMuPDF>=1.24.0

# Development & Testing
pytest>=8.0.0
pytest-mock>=3.12.0
respx>=0.20.0
EOF

# Instalar dependencias una por una para manejar errores
print_header "Instalando dependencias básicas..."
pip install requests click rich python-dotenv Flask Pillow

print_header "Intentando instalar PyMuPDF..."
if pip install PyMuPDF; then
    print_success "PyMuPDF instalado correctamente"
else
    print_warning "PyMuPDF falló al instalar. El análisis de PDF estará limitado."
    print_warning "Puedes intentar instalarlo manualmente más tarde con: pip install PyMuPDF"
fi

print_header "Instalando dependencias de desarrollo..."
pip install pytest pytest-mock respx

print_header "Creando directorios necesarios..."
mkdir -p ~/tmp
mkdir -p ~/.config/chispart

# Crear directorio del proyecto con nuevo nombre
if [ ! -d "$HOME/chispart-cli-llm" ]; then
    print_status "Creando directorio del proyecto..."
    mkdir -p "$HOME/chispart-cli-llm"
fi

print_header "Configurando permisos..."
chmod +x blackbox_cli.py
chmod +x app.py
chmod +x chispart
chmod +x chispart-ui
chmod +x chispart-service

print_header "Creando scripts de conveniencia..."

# Crear directorio bin si no existe
mkdir -p ~/bin

# Script principal CLI
cat > ~/bin/chispart << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm
./chispart "$@"
EOF

# Script para interfaz web básica
cat > ~/bin/chispart-web << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm
echo "🌐 Iniciando Chispart Web UI..."
echo "Accede desde tu navegador en: http://localhost:5000"
echo "Para acceder desde otros dispositivos: http://$(hostname -I | awk '{print $1}'):5000"
echo "Presiona Ctrl+C para detener"
python3 app.py
EOF

# Script para interfaz web automática
cat > ~/bin/chispart-ui << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm
./chispart-ui "$@"
EOF

# Script para gestión de servicio
cat > ~/bin/chispart-service << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm
./chispart-service "$@"
EOF

# Script de configuración
cat > ~/bin/chispart-setup << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm
echo "🔧 Configurando Chispart-CLI-LLM..."
python3 blackbox_cli.py configure
EOF

# Script de estado
cat > ~/bin/chispart-status << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm
./chispart status
EOF

# Hacer ejecutables los scripts
chmod +x ~/bin/chispart
chmod +x ~/bin/chispart-web
chmod +x ~/bin/chispart-ui
chmod +x ~/bin/chispart-service
chmod +x ~/bin/chispart-setup
chmod +x ~/bin/chispart-status

print_header "Creando alias útiles..."
cat >> ~/.bashrc << 'EOF'

# 🚀 Chispart-CLI-LLM Aliases
alias chs='chispart'
alias chs-chat='chispart chat'
alias chs-image='chispart imagen'
alias chs-pdf='chispart pdf'
alias chs-models='chispart modelos'
alias chs-history='chispart historial'
alias chs-interactive='chispart interactivo'

# Alias para interfaz web y servicios
alias chs-ui='chispart-ui'
alias chs-web='chispart-web'
alias chs-service='chispart-service'
alias chs-start='chispart-service start'
alias chs-stop='chispart-service stop'
alias chs-restart='chispart-service restart'
alias chs-logs='chispart-service logs'
alias chs-status='chispart-status'
alias chs-setup='chispart-setup'

EOF

print_success "¡Instalación de Chispart-CLI-LLM completada!"
echo ""
echo "🚀 Chispart-CLI-LLM está listo para usar en Termux"
echo ""
echo "📱 Comandos disponibles:"
echo "  chispart-setup         - Configurar claves API"
echo "  chispart --help        - Ver ayuda completa"
echo "  chispart-ui            - Interfaz web con navegador automático"
echo "  chispart-service       - Gestionar servicio persistente"
echo "  chispart chat 'mensaje' - Enviar mensaje rápido"
echo "  chispart interactivo   - Modo chat interactivo"
echo ""
echo "⚡ Comandos súper cortos (aliases):"
echo "  chs                    - Comando principal"
echo "  chs-ui                 - Interfaz web"
echo "  chs-start              - Iniciar servicio"
echo "  chs-stop               - Detener servicio"
echo "  chs-status             - Estado del sistema"
echo ""
echo "📚 Para empezar:"
echo "  1. Ejecuta: chispart-setup"
echo "  2. Configura tu clave API"
echo "  3. Prueba: chs chat 'Hola, ¿cómo estás?'"
echo "  4. Interfaz web: chs-ui"
echo "  5. Servicio persistente: chs-start"
echo ""
echo "💡 Reinicia tu terminal o ejecuta: source ~/.bashrc"
echo "   para activar los nuevos alias"
echo ""
echo "🌐 Más información:"
echo "   GitHub: https://github.com/SebastianVernisMora/chispart-cli-llm"
echo "   Documentación: README_CHISPART.md"
echo ""
print_success "¡Disfruta usando LLMs desde tu móvil con Chispart! 🎉"