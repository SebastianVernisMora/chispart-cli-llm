#!/bin/bash

# Script de instalación optimizado para Termux
# CLI Universal para LLMs

set -e

echo "🤖 Instalando CLI Universal para LLMs en Termux..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Verificar que estamos en Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "Este script está diseñado para ejecutarse en Termux"
    exit 1
fi

print_status "Actualizando paquetes de Termux..."
pkg update -y

print_status "Instalando dependencias del sistema..."
# Instalar dependencias necesarias para Python y las librerías
pkg install -y python python-pip git libffi openssl libjpeg-turbo libpng zlib freetype

# Dependencias adicionales para PyMuPDF
pkg install -y clang make cmake

print_status "Actualizando pip..."
pip install --upgrade pip setuptools wheel

print_status "Instalando dependencias Python optimizadas para Termux..."

# Crear requirements específicos para Termux
cat > requirements_termux.txt << 'EOF'
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
print_status "Instalando dependencias básicas..."
pip install requests click rich python-dotenv Flask Pillow

print_status "Intentando instalar PyMuPDF..."
if pip install PyMuPDF; then
    print_success "PyMuPDF instalado correctamente"
else
    print_warning "PyMuPDF falló al instalar. El análisis de PDF estará limitado."
    print_warning "Puedes intentar instalarlo manualmente más tarde con: pip install PyMuPDF"
fi

print_status "Instalando dependencias de desarrollo..."
pip install pytest pytest-mock respx

print_status "Creando directorios necesarios..."
mkdir -p ~/tmp
mkdir -p ~/.config/llm-cli

print_status "Configurando permisos..."
chmod +x blackbox_cli.py
chmod +x app.py

print_status "Creando scripts de conveniencia..."

# Script principal CLI
cat > ~/bin/llm-cli << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/cli-universal-llms
python blackbox_cli.py "$@"
EOF

# Script para interfaz web
cat > ~/bin/llm-web << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/cli-universal-llms
echo "🌐 Iniciando interfaz web..."
echo "Accede desde tu navegador en: http://localhost:5000"
echo "Para acceder desde otros dispositivos: http://$(hostname -I | awk '{print $1}'):5000"
echo "Presiona Ctrl+C para detener"
python app.py
EOF

# Script de configuración
cat > ~/bin/llm-setup << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/cli-universal-llms
echo "🔧 Configurando CLI Universal para LLMs..."
python blackbox_cli.py configure
EOF

# Script para UI automática con navegador
cat > ~/bin/blackbox-ui << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/cli-universal-llms
./blackbox-ui "$@"
EOF

# Script para gestión de servicio persistente
cat > ~/bin/blackbox-service << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/cli-universal-llms
./blackbox-service "$@"
EOF

# Hacer ejecutables los scripts
chmod +x ~/bin/llm-cli
chmod +x ~/bin/llm-web
chmod +x ~/bin/llm-setup
chmod +x ~/bin/blackbox-ui
chmod +x ~/bin/blackbox-service

print_status "Creando alias útiles..."
cat >> ~/.bashrc << 'EOF'

# Alias para CLI Universal LLMs
alias llm='llm-cli'
alias llm-chat='llm-cli chat'
alias llm-image='llm-cli imagen'
alias llm-pdf='llm-cli pdf'
alias llm-models='llm-cli modelos'
alias llm-history='llm-cli historial'
alias llm-interactive='llm-cli interactivo'

# Alias para interfaz web y servicios
alias llm-ui='blackbox-ui'
alias llm-service='blackbox-service'
alias llm-start='blackbox-service start'
alias llm-stop='blackbox-service stop'
alias llm-restart='blackbox-service restart'
alias llm-logs='blackbox-service logs'

EOF

print_success "¡Instalación completada!"
echo ""
echo "📱 CLI Universal para LLMs está listo para usar en Termux"
echo ""
echo "🚀 Comandos disponibles:"
echo "  llm-setup          - Configurar claves API"
echo "  llm-cli --help     - Ver ayuda completa"
echo "  llm-web            - Iniciar interfaz web"
echo "  blackbox-ui        - Interfaz web con navegador automático"
echo "  blackbox-service   - Gestionar servicio persistente"
echo "  llm chat 'mensaje' - Enviar mensaje rápido"
echo "  llm-interactive    - Modo chat interactivo"
echo ""
echo "📚 Para empezar:"
echo "  1. Ejecuta: llm-setup"
echo "  2. Configura tu clave API"
echo "  3. Prueba: llm chat 'Hola, ¿cómo estás?'"
echo "  4. Interfaz web: blackbox-ui"
echo "  5. Servicio persistente: blackbox-service start"
echo ""
echo "💡 Reinicia tu terminal o ejecuta: source ~/.bashrc"
echo "   para activar los nuevos alias"
echo ""
print_success "¡Disfruta usando LLMs desde tu móvil! 🎉"