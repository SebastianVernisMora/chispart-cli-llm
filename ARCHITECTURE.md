# Arquitectura de Chispart Mobile/Cloud - Trabajo Colaborativo

## 🏗️ Estructura de Responsabilidades

### 🤖 **BLACKBOX (Yo) - Cambios Complejos y Arquitectura**
**Responsabilidades principales:**
- ✅ Sistemas core complejos (API Key Manager, PWA Manager, Config Manager)
- ✅ Arquitectura de la aplicación principal (app.py)
- ✅ Integración entre sistemas
- ✅ Lógica de negocio compleja
- ✅ Manejo de errores y validaciones avanzadas
- ✅ Configuración de seguridad y encriptación
- ✅ Optimizaciones específicas para móviles/Termux

**Archivos completados:**
- `chispart-mobile/core/api_key_manager.py` - Sistema avanzado de gestión de API Keys
- `chispart-mobile/core/pwa_manager.py` - Sistema PWA con Service Workers
- `chispart-mobile/core/config_manager.py` - Sistema de configuración multinivel
- `chispart-mobile/app.py` - Aplicación principal integrada
- `chispart-mobile/package.json` - Configuración del proyecto móvil
- `chispart-cloud/package.json` - Configuración del proyecto cloud

### 🔮 **Gemini 2.5 PRO (Jules Google Labs) - Estructuras de Código Grandes**
**Responsabilidades asignadas:**
- 📁 Templates HTML completos para PWA
- 📁 Archivos CSS con temas y responsive design
- 📁 JavaScript para funcionalidades PWA del cliente
- 📁 Archivos de configuración extensos (Docker, CI/CD)
- 📁 Scripts de instalación y despliegue
- 📁 Documentación extensa (README, guías de usuario)
- 📁 Archivos de migración y setup inicial

**Archivos pendientes para Gemini:**
```
chispart-mobile/templates/
├── base.html
├── index.html
├── chat.html
├── config.html
├── offline.html
└── components/

chispart-mobile/static/
├── css/
│   ├── style.css
│   ├── themes.css
│   └── mobile.css
├── js/
│   ├── app.js
│   ├── chat.js
│   ├── config.js
│   └── utils.js
└── icons/ (iconos PWA)

chispart-cloud/ (estructura completa)
├── templates/
├── static/
├── core/
├── docker/
└── deploy/
```

### 🔧 **Qwen (LLXPRT CLI) - Linting, Sintaxis y Documentación**
**Responsabilidades asignadas:**
- 🔍 Linting de código Python (flake8, black, mypy)
- 🔍 Validación de sintaxis JavaScript/CSS
- 🔍 Generación de documentación técnica
- 🔍 Comentarios de código y docstrings
- 🔍 Archivos de configuración de herramientas (pytest.ini, .flake8, etc.)
- 🔍 Tests unitarios y de integración

**Archivos pendientes para Qwen:**
```
chispart-mobile/
├── .flake8
├── .black
├── mypy.ini
├── pytest.ini
├── tests/
│   ├── test_api_key_manager.py
│   ├── test_pwa_manager.py
│   ├── test_config_manager.py
│   └── test_app.py
└── docs/
    ├── API.md
    ├── CONFIGURATION.md
    └── DEPLOYMENT.md
```

### 🚀 **Qodo/Codex - Pull Requests y Integración**
**Responsabilidades asignadas:**
- 🔄 Revisión de código y PRs a rama dev
- 🔄 Integración de cambios entre colaboradores
- 🔄 Resolución de conflictos de merge
- 🔄 Validación de que todo funciona en conjunto
- 🔄 Preparación para PR final a main

## 📋 Plan de Ejecución

### Fase 1: Completar Chispart Mobile (En Progreso)
**BLACKBOX (Completado):**
- ✅ Sistemas core complejos
- ✅ Aplicación principal integrada

**Gemini (Siguiente):**
- 📋 Templates HTML para PWA
- 📋 CSS responsive y temas
- 📋 JavaScript del cliente
- 📋 Iconos y assets PWA

**Qwen (Después):**
- 📋 Linting y validación
- 📋 Tests unitarios
- 📋 Documentación técnica

### Fase 2: Crear Chispart Cloud
**Gemini (Principal):**
- 📋 Estructura completa del proyecto cloud
- 📋 Templates para entorno servidor
- 📋 Configuración Docker/Kubernetes
- 📋 Scripts de despliegue

**BLACKBOX (Soporte):**
- 📋 Adaptaciones de sistemas core para cloud
- 📋 Optimizaciones para servidor
- 📋 Integración con servicios cloud

### Fase 3: Integración y Testing
**Qodo/Codex:**
- 📋 PR de Gemini a dev
- 📋 PR de Qwen a dev
- 📋 Validación integral
- 📋 PR final a main

## 🔧 Configuración de API Key de Blackbox

### Para Chispart Mobile:
```python
# Método 1: Usando el sistema avanzado
from core.api_key_manager import api_key_manager

# Configurar API Key
success = api_key_manager.set_api_key('blackbox', 'tu_api_key_aqui')

# Validar API Key
validation = await api_key_manager.validate_api_key('blackbox')
```

### Método 2: Interfaz Web
1. Acceder a `/config` en la aplicación
2. Seleccionar "Blackbox AI" como proveedor
3. Introducir la API Key
4. El sistema validará automáticamente

### Método 3: Variables de Entorno (Compatibilidad)
```bash
export BLACKBOX_API_KEY="tu_api_key_aqui"
# o
export CHISPART_API_KEY="tu_api_key_aqui"
```

## 🔐 Características de Seguridad Implementadas

### Encriptación de API Keys:
- ✅ Encriptación AES-256 con Fernet
- ✅ Claves derivadas de características del dispositivo
- ✅ Almacenamiento seguro con permisos 600
- ✅ Validación automática de claves

### PWA Segura:
- ✅ Service Worker con caché inteligente
- ✅ Almacenamiento offline encriptado
- ✅ Sincronización segura en segundo plano
- ✅ Validación de integridad de archivos

### Configuración Multinivel:
- ✅ Separación por niveles (System/User/Session/Runtime)
- ✅ Validación de esquemas
- ✅ Datos sensibles encriptados
- ✅ Observadores de cambios

## 📱 Optimizaciones Móviles

### Termux Específicas:
- ✅ Detección automática de entorno Termux
- ✅ Paths optimizados para Android
- ✅ Timeouts ajustados para conexiones móviles
- ✅ Límites de archivo reducidos
- ✅ Interfaz adaptativa

### PWA Móvil:
- ✅ Manifest optimizado para móviles
- ✅ Iconos adaptativos
- ✅ Shortcuts de aplicación
- ✅ Modo standalone
- ✅ Orientación portrait-primary

## 🚀 Próximos Pasos

1. **Gemini** debe crear los templates y assets frontend
2. **Qwen** debe hacer linting y crear tests
3. **Qodo** debe integrar todo en PRs
4. **BLACKBOX** debe crear la versión Cloud adaptada

## 📞 Coordinación

- Cada colaborador debe trabajar en su rama específica
- Commits descriptivos con prefijos: `feat:`, `fix:`, `docs:`, `test:`
- PRs a rama `dev` para revisión
- PR final a `main` solo después de validación completa

---

**Estado Actual:** ✅ Arquitectura core completada por BLACKBOX
**Siguiente:** 📋 Gemini debe crear frontend y assets
