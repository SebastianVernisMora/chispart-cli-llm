# 🤖 CLI Universal para LLMs

Una aplicación de línea de comandos (CLI) para interactuar con múltiples APIs de LLM. Permite enviar mensajes de texto, analizar imágenes y procesar documentos PDF usando diferentes proveedores de IA.

## 🚀 Características

- **Múltiples APIs**: Soporte para BlackboxAI, OpenAI, Anthropic, Groq y Together AI
- **Chat de texto**: Envía mensajes y recibe respuestas de cualquier API
- **Análisis de imágenes**: Sube y analiza imágenes (JPG, PNG, WebP) con APIs compatibles
- **Procesamiento de PDFs**: Analiza documentos PDF con APIs compatibles
- **Modo interactivo**: Chat continuo con historial de sesión
- **Múltiples modelos**: Soporte para GPT-4, Claude, Llama, Mixtral, Gemini y más
- **Historial**: Guarda y consulta conversaciones anteriores
- **Interfaz rica**: Output colorido y bien formateado
- **Configuración flexible**: Cambia entre APIs y modelos fácilmente

## 📦 Instalación

1. **Clona o descarga los archivos del proyecto**

2. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configura tu clave API**:
   - Opción 1: Edita `config.py` y reemplaza la clave API
   - Opción 2: Crea un archivo `.env` basado en `.env.example`
   ```bash
   cp .env.example .env
   # Edita .env y agrega tu clave API
   ```

## 🔑 Configuración de API Key

Tu clave API ya está configurada en `config.py`. Si quieres usar variables de entorno:

```bash
export BLACKBOX_API_KEY="tu_clave_api_aqui"
```

## 📖 Uso

### Comandos Básicos

```bash
# Hacer la CLI ejecutable (Linux/Mac)
chmod +x blackbox_cli.py

# Ver ayuda
python blackbox_cli.py --help
```

### 💬 Chat de Texto

```bash
# Mensaje simple
python blackbox_cli.py chat "¿Cuál es la capital de Francia?"

# Con modelo específico
python blackbox_cli.py chat "Explica la fotosíntesis" --modelo gpt-4

# Sin guardar en historial
python blackbox_cli.py chat "Hola mundo" --no-guardar
```

### 🖼️ Análisis de Imágenes

```bash
# Analizar imagen con pregunta por defecto
python blackbox_cli.py imagen foto.jpg

# Con pregunta personalizada
python blackbox_cli.py imagen foto.jpg --prompt "¿Qué colores predominan en esta imagen?"

# Con modelo específico
python blackbox_cli.py imagen foto.jpg --modelo gpt-4-vision
```

### 📄 Procesamiento de PDFs

```bash
# Resumir PDF
python blackbox_cli.py pdf documento.pdf

# Con pregunta específica
python blackbox_cli.py pdf informe.pdf --prompt "¿Cuáles son las conclusiones principales?"

# Con modelo específico
python blackbox_cli.py pdf documento.pdf --modelo gpt-4
```

### 🔄 Modo Interactivo

```bash
# Iniciar chat interactivo
python blackbox_cli.py interactivo

# Con modelo específico
python blackbox_cli.py interactivo --modelo gpt-4-vision
```

En el modo interactivo:
- Escribe `salir`, `exit` o `quit` para terminar
- Escribe `limpiar` o `clear` para limpiar el historial de la sesión
- Usa `Ctrl+C` para interrumpir

### 📊 Historial y Utilidades

```bash
# Ver historial de conversaciones
python blackbox_cli.py historial

# Ver últimas 5 conversaciones
python blackbox_cli.py historial --limite 5

# Listar modelos disponibles
python blackbox_cli.py modelos
```

## 🎯 Ejemplos Prácticos

### Análisis de Código
```bash
python blackbox_cli.py chat "Explica este código Python: print('Hola mundo')"
```

### Análisis de Imagen
```bash
python blackbox_cli.py imagen screenshot.png --prompt "¿Qué aplicación se muestra en esta captura?"
```

### Resumen de Documento
```bash
python blackbox_cli.py pdf contrato.pdf --prompt "Resume los puntos clave de este contrato"
```

### Sesión de Programación
```bash
python blackbox_cli.py interactivo --modelo gpt-4
# Luego puedes hacer preguntas como:
# "¿Cómo creo una función en Python?"
# "Muéstrame un ejemplo de API REST con Flask"
```

## 🔧 Configuración Avanzada

### Modelos Disponibles

- `gpt-4`: Modelo estándar para texto (por defecto)
- `gpt-4-vision`: Para análisis de imágenes
- `gpt-3.5-turbo`: Más rápido y económico

### Formatos de Archivo Soportados

**Imágenes**: JPG, JPEG, PNG, WebP
**Documentos**: PDF

**Límite de tamaño**: 20MB por archivo

### Archivos de Configuración

- `config.py`: Configuración principal
- `.env`: Variables de entorno (opcional)
- `chat_history.json`: Historial de conversaciones (se crea automáticamente)

## 🛠️ Estructura del Proyecto

```
├── blackbox_cli.py      # CLI principal
├── api_client.py        # Cliente de la API
├── config.py           # Configuración
├── utils.py            # Utilidades
├── requirements.txt    # Dependencias
├── .env.example       # Ejemplo de configuración
├── README.md          # Este archivo
└── chat_history.json  # Historial (se crea automáticamente)
```

## 🐛 Solución de Problemas

### Error de Clave API
```
Error: Clave API no configurada
```
**Solución**: Verifica que tu clave API esté correctamente configurada en `config.py` o como variable de entorno.

### Error de Archivo No Encontrado
```
El archivo imagen.jpg no existe
```
**Solución**: Verifica que la ruta del archivo sea correcta y que el archivo exista.

### Error de Formato No Soportado
```
Formato de imagen no soportado
```
**Solución**: Usa archivos JPG, PNG, WebP para imágenes o PDF para documentos.

### Error de Tamaño de Archivo
```
El archivo es demasiado grande
```
**Solución**: Reduce el tamaño del archivo a menos de 20MB.

### Error de Conexión
```
Error de conexión: No se pudo conectar a la API
```
**Solución**: Verifica tu conexión a internet y que la API de BlackboxAI esté disponible.

## 📝 Notas

- Las conversaciones se guardan automáticamente en `chat_history.json`
- El modo interactivo mantiene el contexto durante la sesión
- Los archivos se codifican en base64 antes de enviarlos a la API
- La aplicación muestra información de uso de tokens cuando está disponible

## 🤝 Contribuciones

Si encuentras errores o tienes sugerencias de mejora, no dudes en reportarlos.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
