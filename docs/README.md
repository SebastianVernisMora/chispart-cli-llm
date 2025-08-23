# 🤖 CLI Universal para LLMs (y ahora con Interfaz Web)

Una aplicación para interactuar con múltiples APIs de LLM. Permite enviar mensajes de texto, analizar imágenes y procesar documentos PDF usando diferentes proveedores de IA, tanto desde la línea de comandos (CLI) como desde una cómoda interfaz web.

## 🚀 Características

### Generales
- **Múltiples APIs**: Soporte para BlackboxAI, OpenAI, Anthropic, Groq y Together AI.
- **Múltiples Modelos**: Soporte para GPT-4, Claude, Llama, Mixtral, Gemini y más.
- **Configuración Flexible**: Cambia entre APIs y modelos fácilmente.
- **Historial Centralizado**: Guarda y consulta conversaciones de ambas interfaces en `chat_history.json`.

### Interfaz Web (`app.py`)
- **Interfaz de Chat Moderna**: UI limpia e intuitiva para chatear.
- **Análisis de Archivos**: Sube y analiza imágenes (JPG, PNG, WebP) y documentos PDF.
- **Respuesta en Streaming**: Las respuestas del asistente aparecen palabra por palabra.
- **Renderizado de Markdown**: Las respuestas se muestran con formato, incluyendo resaltado de sintaxis para bloques de código.
- **Historial Interactivo**: Carga y revisa conversaciones pasadas directamente en la interfaz.

### Interfaz de Línea de Comandos (`blackbox_cli.py`)
- **Chat de Texto**: Envía mensajes y recibe respuestas desde la terminal.
- **Análisis de Archivos**: Procesa imágenes y PDFs locales.
- **Modo Interactivo**: Mantén una conversación continua con historial de sesión.
- **Configuración Interactiva**: Un comando `configure` para guardar tus claves de API de forma segura.
- **Interfaz Rica**: Output colorido y bien formateado gracias a `rich`.

## 📦 Instalación

1.  **Clona o descarga los archivos del proyecto.**
2.  **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configura tus claves de API (Recomendado)**:
    Usa el nuevo comando interactivo para configurar tus claves de forma fácil y segura.
    ```bash
    python blackbox_cli.py configure
    ```
    Esto guardará tus claves en un archivo `.env` que la aplicación cargará automáticamente.

## 🔑 Configuración Alternativa

Si prefieres no usar el comando `configure`, puedes crear manualmente un archivo `.env` a partir de `.env.example` o exportar las variables de entorno:

```bash
# Opción 1: Crear archivo .env
cp .env.example .env
# Luego edita el archivo .env con tus claves

# Opción 2: Variables de entorno
export BLACKBOX_API_KEY="tu_clave_aqui"
export OPENAI_API_KEY="tu_clave_aqui"
# etc.
```

## 📖 Uso

### Iniciar la Interfaz Web
Para usar la interfaz web, simplemente ejecuta `app.py`:
```bash
python app.py
```
Luego, abre tu navegador y ve a `http://127.0.0.1:5000`.

### Comandos de la CLI

Primero, haz el script ejecutable (opcional, solo en Linux/Mac):
```bash
chmod +x blackbox_cli.py
```

**Configurar Claves de API (Recomendado)**
```bash
python blackbox_cli.py configure
```

**Ver Ayuda**
```bash
python blackbox_cli.py --help
```

**Chat de Texto**
```bash
python blackbox_cli.py chat "¿Cuál es la capital de Francia?"
```

**Análisis de Imágenes**
```bash
python blackbox_cli.py imagen foto.jpg --prompt "¿Qué colores predominan?"
```

**Análisis de PDFs**
```bash
python blackbox_cli.py pdf documento.pdf --prompt "Resume los puntos clave."
```

**Modo Interactivo**
```bash
python blackbox_cli.py interactivo
```

**Ver Historial y Modelos**
```bash
# Ver historial de conversaciones
python blackbox_cli.py historial

# Listar modelos disponibles para la API por defecto
python blackbox_cli.py modelos
```

## 🛠️ Estructura del Proyecto

```
.
├── app.py               # Backend de la Interfaz Web (Flask)
├── blackbox_cli.py      # Interfaz de Línea de Comandos (Click)
├── static/
│   └── chat_interface.html # Frontend de la Interfaz Web
├── tests/               # Pruebas unitarias (pytest)
├── api_client.py        # Cliente universal para APIs de LLM
├── config.py            # Configuración de APIs y modelos
├── utils.py             # Funciones de utilidad
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Archivos ignorados por Git
├── .env.example         # Ejemplo de archivo de configuración de entorno
└── docs/README.md       # Este archivo

## 🐛 Solución de Problemas

### Error: Clave API no configurada
**Solución**: Asegúrate de haber configurado tu clave de API. La forma más fácil es con el comando `python blackbox_cli.py configure`.

### Error de Archivo No Encontrado
**Solución**: Verifica que la ruta del archivo que pasas como argumento sea correcta y que el archivo exista.

### Error de Conexión
**Solución**: Verifica tu conexión a internet y que los servicios de la API que estás usando estén operativos.

## 🚀 Próximos Pasos y Mejoras Futuras

Este proyecto tiene mucho potencial para seguir creciendo. Algunas ideas para futuras versiones son:

-   **Backend Asíncrono**: Migrar el backend de Flask a un framework completamente asíncrono como FastAPI o Quart para mejorar el rendimiento y la escalabilidad.
-   **Mejoras en el Historial**: Unificar el guardado del historial del modo interactivo para que las sesiones completas se puedan cargar y continuar desde la interfaz web.
-   **Soporte para Más APIs**: Añadir soporte para más proveedores de LLM (e.g., Cohere, Mistral AI).
-   **Despliegue con Docker**: Crear un `Dockerfile` para facilitar el despliegue.
-   **Cobertura de Pruebas Completa**: Ampliar las pruebas para cubrir los endpoints de la API y los comandos de la CLI.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
