#!/bin/bash

# 🚀 Script de migración a Chispart-CLI-LLM
# Actualiza la instalación existente al nuevo branding

echo "🔄 Migrando a Chispart-CLI-LLM..."
echo "================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

# Verificar que estamos en el directorio correcto
if [ ! -f "blackbox_cli.py" ]; then
    print_error "Este script debe ejecutarse desde el directorio del proyecto"
    exit 1
fi

print_header "Iniciando migración a Chispart-CLI-LLM..."

# Backup de configuración existente
print_status "Creando backup de configuración..."
if [ -f ".env" ]; then
    cp .env .env.backup
    print_success "Backup de .env creado"
fi

if [ -f "chat_history.json" ]; then
    cp chat_history.json chat_history.json.backup
    print_success "Backup de historial creado"
fi

# Crear nuevos scripts de Chispart
print_status "Creando nuevos comandos de Chispart..."

# Verificar que los nuevos scripts existen
if [ ! -f "chispart" ] || [ ! -f "chispart-ui" ] || [ ! -f "chispart-service" ]; then
    print_error "Los nuevos scripts de Chispart no se encontraron"
    print_status "Asegúrate de tener los archivos: chispart, chispart-ui, chispart-service"
    exit 1
fi

# Hacer ejecutables los nuevos scripts
chmod +x chispart chispart-ui chispart-service

# Actualizar scripts en ~/bin
print_status "Actualizando scripts en ~/bin..."

mkdir -p ~/bin

# Crear nuevos scripts en ~/bin
cat > ~/bin/chispart << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm 2>/dev/null || cd ~/cli-universal-llms
./chispart "$@"
EOF

cat > ~/bin/chispart-ui << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm 2>/dev/null || cd ~/cli-universal-llms
./chispart-ui "$@"
EOF

cat > ~/bin/chispart-service << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm 2>/dev/null || cd ~/cli-universal-llms
./chispart-service "$@"
EOF

cat > ~/bin/chispart-setup << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm 2>/dev/null || cd ~/cli-universal-llms
echo "🔧 Configurando Chispart-CLI-LLM..."
python3 blackbox_cli.py configure
EOF

cat > ~/bin/chispart-status << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/chispart-cli-llm 2>/dev/null || cd ~/cli-universal-llms
./chispart status
EOF

# Hacer ejecutables
chmod +x ~/bin/chispart*

print_success "Scripts actualizados en ~/bin"

# Actualizar aliases en .bashrc
print_status "Actualizando aliases..."

# Crear backup de .bashrc
cp ~/.bashrc ~/.bashrc.backup

# Remover aliases antiguos si existen
sed -i '/# Alias para CLI Universal LLMs/,/^$/d' ~/.bashrc
sed -i '/# Alias para interfaz web y servicios/,/^$/d' ~/.bashrc

# Agregar nuevos aliases de Chispart
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
alias chs-service='chispart-service'
alias chs-start='chispart-service start'
alias chs-stop='chispart-service stop'
alias chs-restart='chispart-service restart'
alias chs-logs='chispart-service logs'
alias chs-status='chispart-status'
alias chs-setup='chispart-setup'

# Mantener compatibilidad con comandos anteriores
alias llm='chispart'
alias llm-ui='chispart-ui'
alias llm-start='chispart-service start'
alias llm-stop='chispart-service stop'
alias blackbox-ui='chispart-ui'
alias blackbox-service='chispart-service'

EOF

print_success "Aliases actualizados"

# Migrar configuración de servicio si existe
print_status "Migrando configuración de servicio..."

if [ -f "$HOME/.blackbox-ui-service.sh" ]; then
    # Crear nueva configuración de servicio
    sed 's/blackbox/chispart/g' "$HOME/.blackbox-ui-service.sh" > "$HOME/.chispart-ui-service.sh"
    chmod +x "$HOME/.chispart-ui-service.sh"
    print_success "Configuración de servicio migrada"
fi

if [ -f "$HOME/.blackbox-ui-config" ]; then
    cp "$HOME/.blackbox-ui-config" "$HOME/.chispart-ui-config"
    print_success "Configuración migrada"
fi

# Migrar logs si existen
if [ -f "$HOME/.blackbox-ui.log" ]; then
    cp "$HOME/.blackbox-ui.log" "$HOME/.chispart-ui.log"
    print_success "Logs migrados"
fi

# Crear directorio del nuevo proyecto si no existe
print_status "Configurando directorio del proyecto..."

if [ ! -d "$HOME/chispart-cli-llm" ]; then
    print_status "Creando enlace simbólico para compatibilidad..."
    ln -sf "$(pwd)" "$HOME/chispart-cli-llm"
    print_success "Enlace simbólico creado: ~/chispart-cli-llm"
fi

# Actualizar auto-inicio si existe
print_status "Actualizando auto-inicio..."

if grep -q "blackbox-ui-service" ~/.bashrc; then
    sed -i 's/blackbox-ui-service/chispart-ui-service/g' ~/.bashrc
    print_success "Auto-inicio actualizado"
fi

print_success "¡Migración a Chispart-CLI-LLM completada!"
echo ""
echo "🚀 Chispart-CLI-LLM está listo"
echo ""
echo "📱 Nuevos comandos disponibles:"
echo "  chispart               - Comando principal"
echo "  chispart-ui            - Interfaz web automática"
echo "  chispart-service       - Gestión de servicio"
echo "  chispart-setup         - Configuración"
echo "  chispart-status        - Estado del sistema"
echo ""
echo "⚡ Comandos súper cortos:"
echo "  chs                    - Comando principal"
echo "  chs-ui                 - Interfaz web"
echo "  chs-start              - Iniciar servicio"
echo "  chs-stop               - Detener servicio"
echo "  chs-status             - Estado"
echo ""
echo "🔄 Compatibilidad:"
echo "  Los comandos anteriores (llm, blackbox-ui, etc.) siguen funcionando"
echo ""
echo "💡 Reinicia tu terminal o ejecuta: source ~/.bashrc"
echo ""
echo "🎉 ¡Bienvenido a Chispart-CLI-LLM!"