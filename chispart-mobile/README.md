# 🚀 Chispart Mobile - Universal LLM Terminal

**Terminal de IA Universal optimizado para dispositivos móviles y Termux**

Chispart Mobile es una aplicación PWA (Progressive Web App) que te permite interactuar con múltiples APIs de IA desde tu dispositivo móvil, con soporte especial para Termux en Android.

## ✨ Características Principales

- 🤖 **Múltiples APIs**: Blackbox AI, OpenAI, Anthropic, Groq, Together AI
- 📱 **Optimizado para Móviles**: Diseñado específicamente para Termux/Android
- 🔒 **Seguridad Avanzada Opcional**: Encriptación AES-256 para API Keys (requiere `cryptography`).
- 📴 **Modo Offline**: Funciona sin conexión con PWA
- 🎨 **Interfaz Adaptativa**: Temas dark/light, modo compacto
- 🔄 **Sincronización**: Background sync y notificaciones push
- 📊 **Análisis Multimedia**: Soporte para imágenes y PDFs
- ⚡ **Alto Rendimiento**: Optimizado para conexiones móviles

## 🔧 Instalación Rápida

### Para Termux (Android)

```bash
# 1. Instalar dependencias
pkg update && pkg upgrade
pkg install python git

# 2. Clonar repositorio
git clone <tu-repo-url>
cd chispart-mobile

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Ejecutar configuración interactiva
python setup.py
```

### Para Desktop/Servidor

```bash
# 1. Clonar repositorio
git clone <tu-repo-url>
cd chispart-mobile

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar configuración
python setup.py
```

## 🔑 Configuración de API Key de Blackbox

### Método 1: Configuración Interactiva (Recomendado)

```bash
python setup.py
```

El script te guiará paso a paso:

1. **Obtener API Key**:
   - Ve a [https://www.blackbox.ai/api-keys](https://www.blackbox.ai/api-keys)
   - Crea una cuenta o inicia sesión
   - Genera una nueva API Key
   - Copia la clave

2. **Configurar en Chispart**:
   - El script detectará tu entorno automáticamente
   - Te pedirá la API Key de Blackbox (requerida)
   - Validará la clave automáticamente
   - Configurará valores por defecto optimizados

### Método 2: Interfaz Web

1. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

2. Abre tu navegador en `http://localhost:5000`

3. Ve a la página de configuración (`/config`)

4. Selecciona "Blackbox AI" y introduce tu API Key

### Método 3: Variables de Entorno

```bash
# Opción 1: Blackbox API Key
export BLACKBOX_API_KEY="tu_api_key_aqui"

# Opción 2: Chispart API Key (compatibilidad)
export CHISPART_API_KEY="tu_api_key_aqui"

# Ejecutar aplicación
python app.py
```

### Método 4: Archivo .env

Crea un archivo `.env` en el directorio del proyecto:

```env
BLACKBOX_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=tu_openai_key_opcional
ANTHROPIC_API_KEY=tu_anthropic_key_opcional
```

## 🔒 Seguridad de las Claves API

Para proteger tus claves API, Chispart Mobile utiliza dos métodos:

1.  **Encriptación Fuerte (Recomendado)**: Si tienes la librería `cryptography` instalada (`pip install cryptography`), tus claves se guardarán en un archivo local (`api_keys.enc`) encriptadas con el algoritmo AES-256. Esta es la opción más segura.

2.  **Ofuscación Básica (Por defecto en Termux)**: Si `cryptography` no está instalada, la aplicación funcionará igualmente. En este caso, las claves se guardarán en un archivo (`api_keys.json.b64`) codificado en Base64. Esto no es una encriptación real, pero evita que las claves sean legibles a simple vista en el archivo.

Esta dualidad asegura que la aplicación se pueda instalar fácilmente en Termux (donde `cryptography` puede dar problemas) sin sacrificar la seguridad en plataformas que sí lo soportan.

## 🔒 Seguridad de las Claves API

Para proteger tus claves API, Chispart Mobile utiliza dos métodos:

1.  **Encriptación Fuerte (Recomendado)**: Si tienes la librería `cryptography` instalada (`pip install cryptography`), tus claves se guardarán en un archivo local (`api_keys.enc`) encriptadas con el algoritmo AES-256. Esta es la opción más segura.

2.  **Ofuscación Básica (Por defecto en Termux)**: Si `cryptography` no está instalada, la aplicación funcionará igualmente. En este caso, las claves se guardarán en un archivo (`api_keys.json.b64`) codificado en Base64. Esto no es una encriptación real, pero evita que las claves sean legibles a simple vista en el archivo.

Esta dualidad asegura que la aplicación se pueda instalar fácilmente en Termux (donde `cryptography` puede dar problemas) sin sacrificar la seguridad en plataformas que sí lo soportan.

## 🚀 Uso

### Inicio Rápido

```bash
# Termux
./start-termux.sh
# o usar alias (si se configuró)
chispart

# Desktop
./start.sh
# o directamente
python app.py
```

### Acceso Web

- **Local**: `http://localhost:5000`
- **Red local**: `http://[tu-ip]:5000` (para acceso desde otros dispositivos)

### Comandos CLI (Compatibilidad)

```bash
# Chat básico
python -c "from chispart_cli import cli; cli()" chat "Hola, ¿cómo estás?"

# Análisis de imagen
python -c "from chispart_cli import cli; cli()" imagen imagen.jpg --prompt "Describe esta imagen"

# Modo interactivo
python -c "from chispart_cli import cli; cli()" interactivo
```

## 📱 Características Móviles

### Optimizaciones para Termux

- ✅ **Detección automática** de entorno Termux
- ✅ **Paths optimizados** para Android
- ✅ **Timeouts ajustados** para conexiones móviles
- ✅ **Límites de archivo** reducidos para ahorrar datos
- ✅ **Interfaz compacta** para pantallas pequeñas

### PWA (Progressive Web App)

- 📱 **Instalable** como app nativa
- 📴 **Funciona offline** con caché inteligente
- 🔄 **Sincronización** automática en segundo plano
