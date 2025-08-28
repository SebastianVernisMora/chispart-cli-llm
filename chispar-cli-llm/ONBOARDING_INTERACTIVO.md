# 🚀 Onboarding Interactivo - Chispart Dev Agent v3.0

<p align="center">
  <img src="https://img.shields.io/badge/🎯-Onboarding_Interactivo-00D4FF?style=for-the-badge&logo=rocket&logoColor=white" alt="Onboarding">
  <img src="https://img.shields.io/badge/⚡-Setup_Automático-00FF88?style=for-the-badge&logo=lightning&logoColor=white" alt="Auto Setup">
  <img src="https://img.shields.io/badge/🤖-100+_Modelos_IA-FF6B00?style=for-the-badge&logo=brain&logoColor=white" alt="AI Models">
</p>

<div align="center">

## 🎉 ¡Bienvenido a Chispart Dev Agent!

**Tu asistente de desarrollo con IA más poderoso**

</div>

---

## 🚀 Inicio Rápido (1 Minuto)

### Opción 1: Setup Automático Completo ⚡

```bash
# 🔥 Instalación y configuración en UN SOLO COMANDO
curl -fsSL https://raw.githubusercontent.com/tu-usuario/chispar-cli-llm/main/install-enhanced.sh | bash

# O si ya tienes el repositorio clonado:
cd chispar-cli-llm
./install-enhanced.sh --interactive
```

### Opción 2: Setup Guiado Paso a Paso 🎯

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/chispar-cli-llm.git
cd chispar-cli-llm

# 2. Ejecutar wizard interactivo
python setup-wizard.py
```

---

## 🎯 Tutorial Interactivo

### Paso 1: Verificación del Sistema 🔍

Ejecuta el diagnóstico automático:

```bash
./chispart diagnostico
```

**¿Qué hace este comando?**
- ✅ Verifica dependencias Python
- ✅ Comprueba permisos de archivos
- ✅ Detecta entorno (Termux/Desktop)
- ✅ Valida configuración de red

### Paso 2: Configuración de APIs 🔑

#### Configuración Interactiva (Recomendado)

```bash
./chispart config --interactivo
```

**El wizard te guiará para:**
1. **Seleccionar APIs principales** (mínimo 1 requerida)
2. **Obtener API Keys** con enlaces directos
3. **Validar conexiones** en tiempo real
4. **Configurar preferencias** por defecto

#### APIs Disponibles:

| API | Modelos | Obtener Key | Especialidad |
|-----|---------|-------------|--------------|
| 🚀 **Chispart** | 60+ | [Obtener Key](https://chispart.ai/api) | General, Código |
| 🧠 **Qwen AI** | 13 | [Obtener Key](https://dashscope.aliyun.com) | Multilingüe |
| 💎 **Gemini** | 8 | [Obtener Key](https://makersuite.google.com/app/apikey) | Multimodal |
| ⚡ **Codestral** | 5 | [Obtener Key](https://console.mistral.ai) | Programación |

#### Configuración Manual Rápida

```bash
# Configurar API principal (Chispart recomendado)
export CHISPART_API_KEY="tu_clave_aqui"

# Verificar configuración
./chispart config --verificar
```

### Paso 3: Primer Chat con IA 💬

```bash
# Chat básico
./chispart chat "¡Hola! Soy nuevo en Chispart"

# Chat con API específica
./chispart chat "Explícame Python" --api qwen

# Chat con perfil especializado
./chispart chat "Optimizar base de datos" --perfil backend
```

### Paso 4: Explorar Comandos Principales ⚡

#### 🤖 Chat y Conversación
```bash
# Chat interactivo
./chispart chat

# Chat con contexto de archivo
./chispart chat "Revisa este código" --archivo mi_script.py

# Chat con múltiples APIs
./chispart chat "Compara soluciones" --apis chispart,qwen
```

#### ⚡ Ejecución Segura de Comandos
```bash
# Ejecutar comando con validación
./chispart execute "git status"

# Ejecutar con confirmación
./chispart execute "npm install" --confirm

# Modo seguro (solo comandos whitelist)
./chispart execute "ls -la" --safe
```

#### 👥 Gestión de Equipos
```bash
# Listar equipos disponibles
./chispart equipos

# Crear nuevo equipo
./chispart equipos --crear "mi-proyecto-web"

# Trabajar con equipo específico
./chispart equipos --usar "mi-proyecto-web"
```

#### 🆘 Asistencia Técnica (ATC)
```bash
# Diagnóstico automático
./chispart atc

# Ayuda interactiva
./chispart atc --interactivo

# Solución de problema específico
./chispart atc --problema "error-dependencias"
```

### Paso 5: Personalización Avanzada 🎨

#### Configurar Perfil de Desarrollador

```bash
# Ver perfiles disponibles
./chispart perfiles

# Configurar perfil por defecto
./chispart config --perfil frontend

# Crear perfil personalizado
./chispart perfiles --crear "mi-perfil-custom"
```

#### Perfiles Disponibles:
- 🎨 **Frontend**: React, Vue, Angular, UI/UX
- ⚙️ **Backend**: APIs, Bases de datos, Microservicios
- 📱 **Mobile**: React Native, Flutter, iOS, Android
- 🤖 **DevOps**: Docker, Kubernetes, CI/CD, Cloud
- 🔒 **Security**: Pentesting, Auditorías, Compliance
- 📊 **Data**: ML, Analytics, Big Data, ETL
- 🏗️ **Architect**: Diseño de sistemas, Patrones

#### Configurar Seguridad

```bash
# Ver configuración de seguridad actual
./chispart config --seguridad

# Cambiar nivel de seguridad
./chispart config --seguridad-nivel alto

# Personalizar whitelist/blacklist
./chispart config --comandos-seguros
```

---

## 🎓 Casos de Uso Prácticos

### Caso 1: Desarrollo Web Frontend 🎨

```bash
# 1. Configurar perfil frontend
./chispart config --perfil frontend

# 2. Crear proyecto React
./chispart chat "Crear estructura de proyecto React con TypeScript"

# 3. Ejecutar comandos de desarrollo
./chispart execute "npx create-react-app mi-app --template typescript" --confirm

# 4. Obtener ayuda específica
./chispart chat "Mejores prácticas para componentes React" --perfil frontend
```

### Caso 2: Análisis de Código Backend ⚙️

```bash
# 1. Configurar perfil backend
./chispart config --perfil backend

# 2. Analizar archivo de código
./chispart chat "Revisa este API endpoint" --archivo api/users.py

# 3. Optimización de base de datos
./chispart chat "Optimizar consultas SQL" --perfil backend --api codestral
```

### Caso 3: DevOps y Deployment 🤖

```bash
# 1. Configurar perfil DevOps
./chispart config --perfil devops

# 2. Crear configuración Docker
./chispart chat "Crear Dockerfile para aplicación Node.js"

# 3. Ejecutar comandos Docker de forma segura
./chispart execute "docker build -t mi-app ." --confirm
```

---

## 🔧 Troubleshooting Interactivo

### Problemas Comunes y Soluciones

#### ❌ Error: "API Key no válida"

```bash
# Diagnóstico automático
./chispart diagnostico --api

# Reconfigurar API
./chispart config --reconfigurar-api chispart

# Verificar conectividad
./chispart config --test-conexion
```

#### ❌ Error: "Comando no encontrado"

```bash
# Verificar instalación
./chispart version --completo

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# Verificar permisos
chmod +x chispart chs
```

#### ❌ Error: "Timeout de conexión"

```bash
# Para Termux/móviles (timeouts más largos)
./chispart config --timeout 120

# Verificar conexión de red
./chispart diagnostico --red

# Usar API alternativa
./chispart chat "test" --api qwen
```

### Diagnóstico Automático Completo

```bash
# Ejecutar diagnóstico completo
./chispart diagnostico --completo

# Generar reporte de sistema
./chispart diagnostico --reporte > diagnostico.txt

# Enviar reporte para soporte
./chispart atc --enviar-reporte diagnostico.txt
```

---

## 📚 Recursos Adicionales

### Documentación Completa
- 📖 [Guía de Comandos Completa](docs/GUIA_COMANDOS.md)
- 🔧 [Troubleshooting Avanzado](docs/TROUBLESHOOTING.md)
- 🏗️ [Arquitectura del Sistema](docs/CHISPART_DEV_AGENT_V3_COMPLETADO.md)

### Scripts Útiles
```bash
# Ver todos los comandos disponibles
./chispart ayuda --completo

# Exportar configuración
./chispart config --exportar > mi-config.json

# Importar configuración
./chispart config --importar mi-config.json

# Actualizar a última versión
./chispart actualizar
```

### Atajos y Aliases
```bash
# Usar alias corto
./chs chat "Hola"

# Configurar aliases personalizados
./chispart config --aliases

# Aliases recomendados:
alias cc="./chispart chat"
alias ce="./chispart execute"
alias ca="./chispart atc"
```

---

## 🎯 Próximos Pasos

### 1. Explorar Funcionalidades Avanzadas
- 🔄 **Split Chat**: Conversaciones paralelas
- 🔀 **Merge Chat**: Combinar conversaciones
- 📊 **Analytics**: Estadísticas de uso
- 🔌 **Plugins**: Extensiones personalizadas

### 2. Integración con Herramientas
- 🔗 **Git Integration**: Commits inteligentes
- 📝 **IDE Plugins**: VSCode, Vim, Emacs
- 🐳 **Docker Support**: Contenedores automáticos
- ☁️ **Cloud Deploy**: Despliegue automático

### 3. Comunidad y Soporte
- 💬 **Discord**: [Únete a la comunidad](https://discord.gg/chispart)
- 📧 **Email**: soporte@chispart.ai
- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/chispar-cli-llm/issues)
- 📖 **Wiki**: [Documentación Wiki](https://github.com/tu-usuario/chispar-cli-llm/wiki)

---

<div align="center">

## 🎉 ¡Felicidades!

**Ya tienes Chispart Dev Agent configurado y listo para usar**

### Comando de Prueba Final:

```bash
./chispart chat "¡Estoy listo para desarrollar con IA!"
```

**¿Necesitas ayuda?** Ejecuta: `./chispart atc --interactivo`

---

**Desarrollado con ❤️ por Sebastian Vernis | Soluciones Digitales**

[🏠 Inicio](README.md) | [📖 Documentación](docs/) | [🆘 Soporte](docs/TROUBLESHOOTING.md)

</div>
