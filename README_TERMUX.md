# 📱 CLI Universal para LLMs - Edición Termux

Una versión optimizada del CLI Universal para LLMs específicamente diseñada para **Termux** en dispositivos Android. Disfruta de la potencia de múltiples APIs de IA directamente desde tu móvil.

## 🚀 Instalación Rápida en Termux

### Paso 1: Preparar Termux
```bash
# Actualizar Termux
pkg update && pkg upgrade

# Instalar Git si no lo tienes
pkg install git
```

### Paso 2: Clonar e Instalar
```bash
# Clonar el repositorio
git clone https://github.com/SebastianVernisMora/cli-universal-llms.git
cd cli-universal-llms

# Ejecutar instalación automática para Termux
./install_termux.sh
```

### Paso 3: Configurar
```bash
# Configurar tu primera API key
llm-setup

# Verificar que todo funciona
llm-status
```

## 🎯 Comandos Optimizados para Móvil

### Comandos Rápidos
```bash
# Chat rápido
llm chat "¿Cuál es la capital de Francia?"

# Modo interactivo (ideal para móviles)
llm-interactive

# Analizar imagen desde tu galería
llm imagen ~/storage/shared/Pictures/foto.jpg

# Analizar PDF desde descargas
llm pdf ~/storage/shared/Download/documento.pdf

# Ver modelos disponibles
llm modelos

# Ver historial de conversaciones
llm historial
```

### Interfaz Web Móvil
```bash
# Iniciar interfaz web optimizada para móvil
llm-web

# Interfaz web con navegador automático
blackbox-ui

# Servicio persistente (sigue funcionando aunque cierres Termux)
blackbox-service start

# Acceder desde el navegador:
# http://localhost:5000
```

## 📱 Características Específicas para Termux

### ✅ Optimizaciones Implementadas

- **🔧 Instalación Automática**: Script que maneja todas las dependencias
- **📁 Paths Optimizados**: Usa directorios correctos de Termux automáticamente
- **⚡ Timeouts Ajustados**: Configurados para conexiones móviles
- **💾 Archivos Temporales**: Manejo inteligente de archivos temporales
- **🖥️ Interfaz Adaptada**: Ancho de consola optimizado para pantallas pequeñas
- **🌐 Red Optimizada**: Mejor manejo de conexiones lentas o inestables
- **📊 Límites Ajustados**: Tamaños de archivo optimizados para móviles

### 🎨 Interfaz Optimizada

- **Rich Formatting**: Salida colorida y bien formateada
- **Tablas Compactas**: Información organizada para pantallas pequeñas
- **Mensajes Claros**: Errores y sugerencias específicas para móviles
- **Navegación Fácil**: Comandos cortos y memorables

## 🔧 Configuración Avanzada

### Acceso a Archivos del Teléfono
```bash
# Configurar acceso al almacenamiento del teléfono
termux-setup-storage

# Ubicaciones útiles:
# ~/storage/shared/          - Almacenamiento principal
# ~/storage/shared/Pictures/ - Fotos
# ~/storage/shared/Download/ - Descargas
# ~/storage/shared/Documents/- Documentos
```

### Variables de Entorno
```bash
# Ver ubicaciones configuradas
llm-status

# Configurar APIs manualmente (opcional)
export OPENAI_API_KEY="tu_clave_aqui"
export ANTHROPIC_API_KEY="tu_clave_aqui"
```

## 🛠️ Solución de Problemas

### Problemas Comunes

#### PyMuPDF no se instala
```bash
# Instalar dependencias de compilación
pkg install clang make cmake

# Intentar instalar PyMuPDF
pip install PyMuPDF

# Si falla, el análisis de PDF estará limitado pero el resto funcionará
```

#### Errores de Conexión
```bash
# Verificar conexión
ping google.com

# Cambiar de WiFi a datos móviles o viceversa
# Los timeouts están optimizados para conexiones lentas
```

#### Archivos Temporales
```bash
# Limpiar archivos temporales si hay problemas de espacio
rm -rf ~/tmp/*

# El sistema creará el directorio automáticamente
```

#### Permisos de Archivos
```bash
# Dar permisos de ejecución si es necesario
chmod +x llm-cli llm-web llm-status

# Verificar permisos de archivos
ls -la ~/storage/shared/
```

### Comandos de Diagnóstico

```bash
# Estado completo del sistema
llm-status

# Verificar dependencias
python -c "import requests, click, rich, flask; print('✅ Dependencias OK')"

# Verificar APIs configuradas
llm modelos

# Probar conexión básica
llm chat "test"
```

## 📊 Rendimiento en Móviles

### Límites Optimizados
- **Imágenes**: Máximo 10MB (vs 20MB en desktop)
- **PDFs**: Máximo 15MB (vs 20MB en desktop)
- **Texto**: Máximo 50,000 caracteres (vs 100,000 en desktop)

### Consejos de Rendimiento
- Usa WiFi cuando sea posible para mejor velocidad
- El modo interactivo es más eficiente que comandos individuales
- La interfaz web consume menos batería que el CLI intensivo
- Cierra otras apps para liberar memoria

## 🔧 Gestión de Servicio Persistente

### Comandos de Servicio
```bash
# Iniciar servicio persistente
blackbox-service start

# Detener servicio
blackbox-service stop

# Reiniciar servicio
blackbox-service restart

# Ver estado del servicio
blackbox-service status

# Ver logs en tiempo real
blackbox-service logs

# Configurar auto-inicio
blackbox-service setup-autostart

# Iniciar monitor automático (reinicia si se cae)
blackbox-service monitor-start
```

### Interfaz Web Automática
```bash
# Lanzar interfaz web con navegador automático
blackbox-ui

# Lanzar como servicio persistente
blackbox-ui --service-start

# Ver estado del servicio
blackbox-ui --service-status

# Detener servicio
blackbox-ui --service-stop
```

## 🎆 Ejemplos de Uso Móvil

### Análisis de Fotos
```bash
# Analizar foto recién tomada
llm imagen ~/storage/shared/DCIM/Camera/IMG_latest.jpg "¿Qué hay en esta foto?"

# Analizar screenshot
llm imagen ~/storage/shared/Pictures/Screenshots/screenshot.png "Explica lo que ves"
```

### Trabajo con Documentos
```bash
# Resumir PDF descargado
llm pdf ~/storage/shared/Download/articulo.pdf "Resume los puntos principales"

# Analizar documento de trabajo
llm pdf ~/storage/shared/Documents/informe.pdf "¿Cuáles son las conclusiones?"
```

### Chat Productivo
```bash
# Sesión de trabajo
llm-interactive

# En la sesión:
# > "Ayúdame a escribir un email profesional"
# > "Traduce esto al inglés: [texto]"
# > "Explica este concepto de programación"
```

## 🔄 Actualizaciones

```bash
# Actualizar el proyecto
cd ~/cli-universal-llms
git pull origin main

# Reinstalar dependencias si es necesario
pip install -r requirements.txt

# Verificar que todo funciona
llm-status
```

## 💡 Tips y Trucos

### Productividad
- Usa alias personalizados en `~/.bashrc`
- Configura múltiples APIs para redundancia
- Guarda comandos frecuentes en scripts

### Batería
- La interfaz web es más eficiente para sesiones largas
- Usa modo avión + WiFi para ahorrar batería
- Cierra la app cuando no la uses

### Almacenamiento
- Limpia el historial periódicamente: `rm chat_history.json`
- Usa archivos temporales para análisis únicos
- Comprime PDFs grandes antes de analizarlos

## 🆘 Soporte

Si encuentras problemas específicos de Termux:

1. **Ejecuta**: `llm-status` para diagnóstico
2. **Verifica**: Conexión a internet y permisos
3. **Consulta**: Los logs en `~/.config/llm-cli/`
4. **Reporta**: Issues en el repositorio de GitHub

---

## 🎉 ¡Disfruta de la IA en tu móvil!

Con esta optimización para Termux, tienes acceso completo a múltiples APIs de IA directamente desde tu dispositivo Android. ¡Perfecto para productividad móvil, aprendizaje, y experimentación con IA!

**¿Listo para empezar?** Ejecuta `llm-setup` y comienza a chatear con IA desde tu móvil. 🚀