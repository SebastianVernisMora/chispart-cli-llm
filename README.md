<p align="center">
  <img src="https://raw.githubusercontent.com/SebastianVernisMora/chispart-cli-llm/main/assets/logo.png" alt="Chispart CLI Logo" width="100%">
</p>

<h1 align="center">🚀 Chispart CLI – Interfaz Conversacional con IA Híbrida </h1>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue?style=for-the-badge&logo=git&logoColor=0A0A0A&labelColor=1A1A1A" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge&logo=open-source-initiative&logoColor=0A0A0A&labelColor=1A1A1A" alt="License">
  <img src="https://img.shields.io/badge/status-active-success?style=for-the-badge&logo=statuspage&logoColor=0A0A0A&labelColor=1A1A1A" alt="Status">
  <img src="https://img.shields.io/badge/contributions-welcome-orange?style=for-the-badge&logo=github&logoColor=0A0A0A&labelColor=1A1A1A" alt="Contributions Welcome">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Chispart-CLI--LLM-00FF88?style=for-the-badge&logo=terminal&logoColor=0A0A0A&labelColor=1A1A1A" alt="Chispart CLI">
  <img src="https://img.shields.io/badge/Mobile-Optimized-BB88FF?style=for-the-badge&logo=android&logoColor=0A0A0A&labelColor=1A1A1A" alt="Mobile Optimized">
  <img src="https://img.shields.io/badge/Universal-AI--Access-FF88BB?style=for-the-badge&logo=openai&logoColor=0A0A0A&labelColor=1A1A1A" alt="Universal AI Access">
  <img src="https://img.shields.io/badge/Style-Neon--Powered-88FFFF?style=for-the-badge&logo=lightning&logoColor=0A0A0A&labelColor=1A1A1A" alt="Neon Style">
</p>


**Chispart-CLI-LLM** es la solución definitiva para acceder a múltiples APIs de LLM desde tu dispositivo móvil. Optimizado específicamente para **Termux** en Android, ofrece una experiencia de terminal profesional con interfaz web moderna.

## ✨ **¿Qué es Chispart?**

Chispart democratiza el acceso a la inteligencia artificial, llevando la potencia de múltiples LLMs directamente a tu móvil. Con una instalación de un solo comando y una interfaz intuitiva, puedes chatear, analizar imágenes y procesar documentos PDF usando las mejores APIs del mercado.

### 🎯 **Características Principales**

- 🌐 **Acceso Universal**: OpenAI, Anthropic, Groq, Together AI, BlackboxAI en un solo lugar
- 📱 **Optimizado para Móviles**: Diseñado específicamente para Termux/Android
- ⚡ **Instalación Rápida**: Un comando y listo para usar
- 🔄 **Servicio Persistente**: Funciona aunque cierres la aplicación
- 🎨 **Interfaz Dual**: CLI potente + interfaz web moderna
- 🖼️ **Análisis de Imágenes**: Sube fotos directamente desde tu galería
- 📄 **Procesamiento de PDFs**: Analiza documentos sobre la marcha
- 🛡️ **Robusto y Confiable**: Monitor automático y recuperación de errores

## 🚀 **Instalación Rápida**

### Para Termux (Android)

```bash
# 1. Clonar el repositorio
git clone https://github.com/SebastianVernisMora/chispart-cli-llm.git
cd chispart-cli-llm

# 2. Instalar en un comando
./install_chispart.sh

# 3. Configurar tu primera API
chispart-setup

# 4. ¡Empezar a usar!
chs chat "¡Hola desde mi móvil!"
```

### Para otros sistemas

```bash
# Instalación estándar
git clone https://github.com/SebastianVernisMora/chispart-cli-llm.git
cd chispart-cli-llm
pip install -r requirements.txt

# Configurar
python chispart_cli.py configure
```

## 📱 **Comandos Principales**

### 🎯 **Comandos Básicos**
```bash
# Chat rápido
chispart chat "¿Cuál es la capital de Francia?"
chs chat "Explícame la física cuántica"

# Modo interactivo
chispart interactivo
chs-interactive

# Analizar imagen
chispart imagen foto.jpg "¿Qué hay en esta imagen?"
chs-image ~/storage/shared/Pictures/screenshot.png

# Analizar PDF
chispart pdf documento.pdf "Resume este documento"
chs-pdf ~/storage/shared/Download/paper.pdf
```

### 🌐 **Interfaz Web**
```bash
# Interfaz web con navegador automático
chispart-ui
chs-ui

# Interfaz web básica
chispart-web
chs-web
```

### 🔧 **Gestión de Servicio**
```bash
# Iniciar servicio persistente
chispart-service start
chs-start

# Ver estado
chispart-service status
chs-status

# Ver logs en tiempo real
chispart-service logs
chs-logs

# Detener servicio
chispart-service stop
chs-stop
```

## 🎨 **Interfaz Web Moderna**

Chispart incluye una interfaz web completamente optimizada para móviles:

- 📱 **Responsive Design**: Perfecto para pantallas pequeñas
- 🌙 **Dark Mode**: Fácil para los ojos
- ⚡ **Streaming en Tiempo Real**: Respuestas que aparecen mientras se generan
- 📁 **Upload de Archivos**: Arrastra y suelta imágenes y PDFs
- 💾 **Historial Persistente**: Todas tus conversaciones guardadas
- 🔄 **Auto-reconexión**: Se reconecta automáticamente si se pierde la conexión

### Acceso a la Interfaz Web

```bash
# Lanzar con navegador automático
chs-ui

# URLs de acceso:
# Local: http://localhost:5000
# Red: http://[tu-ip]:5000
```

## 🤖 **APIs Soportadas**

| API | Modelos Disponibles | Características |
|-----|-------------------|-----------------|
| **OpenAI** | GPT-4, GPT-3.5, GPT-4 Vision | Chat, imágenes, función calling |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Haiku | Chat avanzado, análisis profundo |
| **Groq** | Llama 3, Mixtral, Gemma | Velocidad ultra-rápida |
| **Together AI** | Llama 3, Qwen, Code Llama | Modelos open source |
| **BlackboxAI** | Blackbox, GPT-4 | Programación y código |

## 📱 **Optimizaciones para Móviles**

### ⚡ **Rendimiento**
- **Timeouts Adaptativos**: 120s para móviles vs 30s desktop
- **Límites Optimizados**: Archivos más pequeños para conexiones lentas
- **Streaming Inteligente**: Chunks optimizados para móviles
- **Caché Local**: Respuestas frecuentes guardadas localmente

### 🔋 **Batería**
- **Modo Producción**: Debug desactivado para ahorrar batería
- **Suspensión Inteligente**: Pausa automática en inactividad
- **Optimización de Red**: Menos requests, más eficiencia

### 📁 **Almacenamiento**
- **Paths Seguros**: Compatible con sistema de archivos de Termux
- **Limpieza Automática**: Archivos temporales se eliminan automáticamente
- **Compresión de Logs**: Rotación automática para ahorrar espacio

## 🛡️ **Características Avanzadas**

### 🔄 **Servicio Persistente**
```bash
# El servicio sigue funcionando aunque cierres Termux
chs-start

# Monitor automático reinicia si se cae
chispart-service monitor-start

# Auto-inicio al abrir Termux
chispart-service setup-autostart
```

### 📊 **Monitoreo y Logs**
```bash
# Estado detallado con métricas
chs-status

# Logs en tiempo real
chs-logs

# Limpiar logs antiguos
chispart-service clean-logs
```

### ⚙️ **Configuración Avanzada**
```bash
# Editar configuración del servicio
chispart-service config

# Configurar múltiples APIs
chispart-setup

# Ver modelos disponibles
chispart modelos
```

## 📚 **Casos de Uso**

### 👨‍💻 **Para Desarrolladores**
```bash
# Revisar código
chs chat "Revisa este código Python: [código]"

# Generar documentación
chs chat "Crea documentación para esta función"

# Debug de errores
chs chat "¿Por qué falla este código? [error]"
```

### 🎓 **Para Estudiantes**
```bash
# Explicar conceptos
chs chat "Explícame la teoría de la relatividad"

# Analizar documentos académicos
chs-pdf paper.pdf "Resume los puntos principales"

# Ayuda con tareas
chs-interactive  # Sesión de estudio
```

### 💼 **Para Profesionales**
```bash
# Analizar documentos de trabajo
chs-pdf informe.pdf "¿Cuáles son las conclusiones?"

# Procesar imágenes de presentaciones
chs-image slide.jpg "Extrae el texto de esta diapositiva"

# Productividad móvil
chs-ui  # Interfaz web para trabajo remoto
```

### 🔬 **Para Investigadores**
```bash
# Análisis de datos
chs chat "Analiza estos resultados estadísticos"

# Revisión de literatura
chs-pdf articulo.pdf "Identifica la metodología usada"

# Procesamiento de imágenes científicas
chs-image grafico.png "Describe los datos en este gráfico"
```

## 🔧 **Configuración**

### 🔑 **Configurar APIs**
```bash
# Configuración interactiva
chispart-setup

# O editar manualmente
nano .env
```

### 📁 **Acceso a Archivos del Teléfono**
```bash
# Configurar acceso al almacenamiento
termux-setup-storage

# Ubicaciones útiles:
# ~/storage/shared/Pictures/    - Fotos
# ~/storage/shared/Download/    - Descargas
# ~/storage/shared/Documents/   - Documentos
```

### ⚙️ **Variables de Entorno**
```bash
# APIs soportadas
OPENAI_API_KEY="tu_clave_openai"
ANTHROPIC_API_KEY="tu_clave_anthropic"
GROQ_API_KEY="tu_clave_groq"
TOGETHER_API_KEY="tu_clave_together"
BLACKBOX_API_KEY="tu_clave_blackbox"
```

## 🛠️ **Solución de Problemas**

### ❓ **Problemas Comunes**

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

# Los timeouts están optimizados para conexiones lentas
# Cambiar de WiFi a datos móviles o viceversa
```

#### Servicio no inicia
```bash
# Verificar estado
chs-status

# Ver logs de error
chs-logs

# Reiniciar servicio
chs-restart
```

### 🔍 **Diagnóstico**
```bash
# Estado completo del sistema
chs-status

# Verificar dependencias
python3 -c "import requests, click, rich, flask; print('✅ OK')"

# Probar conexión básica
chs chat "test"
```

## 📈 **Roadmap**

### 🔴 **Próxima Versión (v2.1)**
- [ ] Tests automatizados para Termux
- [ ] Sistema de actualización inteligente
- [ ] Validación post-instalación mejorada

### 🟡 **Versión Futura (v2.2)**
- [ ] Integración con Termux:API para notificaciones
- [ ] Modo offline con caché
- [ ] Widget de Android

### 🟢 **Largo Plazo (v3.0)**
- [ ] Sincronización entre dispositivos
- [ ] Temas personalizables
- [ ] Internacionalización

## 🤝 **Contribuir**

¡Las contribuciones son bienvenidas!

### 🔧 **Desarrollo**
```bash
# Fork del repositorio
git clone https://github.com/tu-usuario/chispart-cli-llm.git

# Crear rama de feature
git checkout -b feature/nueva-caracteristica

# Hacer cambios y commit
git commit -m "feat: agregar nueva característica"

# Push y crear PR
git push origin feature/nueva-caracteristica
```

### 📋 **Issues y Sugerencias**
- 🐛 **Reportar bugs**: Usa el template de issue
- 💡 **Sugerir features**: Describe el caso de uso
- 📚 **Mejorar docs**: PRs de documentación siempre bienvenidos

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 **Agradecimientos**

- **Termux Team**: Por hacer posible Linux en Android
- **OpenAI, Anthropic, Groq**: Por sus increíbles APIs
- **Comunidad Open Source**: Por las librerías que hacen esto posible

## 📞 **Soporte**

📧 **Email**: [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/SebastianVernisMora/chispart-cli-llm/issues)
- 💬 **Discusiones**: [GitHub Discussions](https://github.com/SebastianVernisMora/chispart-cli-llm/discussions)

---

## 🎉 **¡Empieza Ahora!**

```bash
# Instalación rápida
git clone https://github.com/SebastianVernisMora/chispart-cli-llm.git
cd chispart-cli-llm
./install_chispart.sh

# Primer uso
chispart-setup
chs chat "¡Hola, Chispart!"
```

---

<div align="center">

### 🚀 Chispart-CLI-LLM

_Where Mobile Meets AI, Where Terminal Meets Innovation_

[![GitHub](https://img.shields.io/badge/GitHub-Chispart--CLI--LLM-00FF88?style=for-the-badge&logo=github&logoColor=0A0A0A&labelColor=1A1A1A)](https://github.com/SebastianVernisMora/chispart-cli-llm)
[![Termux](https://img.shields.io/badge/Optimized-Termux-BB88FF?style=for-the-badge&logo=android&logoColor=0A0A0A&labelColor=1A1A1A)](https://termux.com)
[![AI](https://img.shields.io/badge/Universal-AI--Access-FF88BB?style=for-the-badge&logo=openai&logoColor=0A0A0A&labelColor=1A1A1A)](https://openai.com)



<p align="center">
  💻 <em>Convierte tu terminal en un asistente conversacional con IA híbrida.</em><br>
  ⭐ ¡Instala Chispart CLI y lleva tu productividad al siguiente nivel!
</p>
```
</div>
