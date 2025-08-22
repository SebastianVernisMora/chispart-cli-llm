# 🚀 Nuevos Comandos: blackbox-ui y blackbox-service

## 📋 Resumen

Se han agregado dos nuevos comandos poderosos para mejorar la experiencia de uso del CLI Universal para LLMs en Termux:

1. **`blackbox-ui`** - Lanzador inteligente de interfaz web con navegador automático
2. **`blackbox-service`** - Gestor completo de servicio persistente

## 🌐 blackbox-ui - Interfaz Web Automática

### Características Principales

- ✅ **Apertura automática del navegador** (usando `termux-open-url` en Termux)
- ✅ **Detección automática de IP local** para acceso desde otros dispositivos
- ✅ **Configuración optimizada** para móviles (debug off, threading on)
- ✅ **Servicio persistente integrado** (funciona aunque cierres Termux)
- ✅ **Información detallada** de acceso y configuración

### Uso Básico

```bash
# Lanzar interfaz web con navegador automático
blackbox-ui

# Ver ayuda completa
blackbox-ui --help

# Lanzar sin abrir navegador automáticamente
blackbox-ui --no-browser
```

### Gestión de Servicio Integrada

```bash
# Iniciar como servicio persistente
blackbox-ui --service-start

# Ver estado del servicio
blackbox-ui --service-status

# Detener servicio
blackbox-ui --service-stop
```

### Características Avanzadas

- **Auto-detección de Termux**: Aplica optimizaciones específicas automáticamente
- **Creación de servicio persistente**: Genera script de servicio en `~/.blackbox-ui-service.sh`
- **Información de red**: Muestra URLs para acceso local y desde otros dispositivos
- **Consejos contextuales**: Muestra tips específicos para Termux

## 🔧 blackbox-service - Gestor de Servicio Persistente

### Características Principales

- ✅ **Gestión completa del servicio** (start, stop, restart, status)
- ✅ **Monitor automático** con reinicio automático si se cae
- ✅ **Logs en tiempo real** con rotación automática
- ✅ **Auto-inicio configurable** (se inicia al abrir Termux)
- ✅ **Configuración avanzada** editable
- ✅ **Estado detallado** con información de recursos

### Comandos Principales

```bash
# Gestión básica del servicio
blackbox-service start          # Iniciar servicio
blackbox-service stop           # Detener servicio
blackbox-service restart        # Reiniciar servicio
blackbox-service status         # Ver estado detallado

# Monitoreo y logs
blackbox-service logs           # Ver logs en tiempo real
blackbox-service clean-logs     # Limpiar archivos de log
blackbox-service monitor-start  # Iniciar monitor automático
blackbox-service monitor-stop   # Detener monitor automático

# Configuración avanzada
blackbox-service setup-autostart # Configurar auto-inicio
blackbox-service config         # Editar configuración
```

### Estado Detallado

El comando `blackbox-service status` muestra:

- 📊 **Estado del servicio** (ejecutándose/detenido con PID)
- 🔍 **Estado del monitor** automático
- 💾 **Uso de recursos** (CPU, RAM)
- ⏱️ **Tiempo de actividad**
- 📁 **Ubicación de archivos** (logs, config, PID)
- 🌐 **URLs de acceso** (local y red)

### Monitor Automático

El monitor automático:
- ✅ Verifica cada 30 segundos si el servicio está ejecutándose
- ✅ Reinicia automáticamente si se detecta que se cayó
- ✅ Limita los intentos de reinicio (máximo 5 por defecto)
- ✅ Registra todos los eventos en el log
- ✅ Se puede configurar el intervalo y límites

### Configuración Avanzada

Archivo de configuración: `~/.blackbox-ui-config`

```bash
# Configuración del servicio BlackboxAI UI
AUTO_START=true                 # Auto-inicio al abrir Termux
AUTO_RESTART=true              # Reinicio automático si se cae
MONITOR_INTERVAL=30            # Intervalo de verificación (segundos)
MAX_RESTART_ATTEMPTS=5         # Máximo intentos de reinicio
RESTART_DELAY=10               # Delay entre reintentos (segundos)
ENABLE_LOGGING=true            # Habilitar logging
LOG_ROTATION=true              # Rotación automática de logs
MAX_LOG_SIZE=10M               # Tamaño máximo de logs
```

## 🎯 Casos de Uso

### Uso Casual - Interfaz Rápida

```bash
# Simplemente abrir la interfaz web
blackbox-ui
# ✅ Se abre automáticamente el navegador
# ✅ Listo para usar inmediatamente
```

### Uso Productivo - Servicio Persistente

```bash
# Configurar servicio persistente
blackbox-service start
blackbox-service monitor-start
blackbox-service setup-autostart

# ✅ Servicio siempre disponible
# ✅ Se reinicia automáticamente si se cae
# ✅ Se inicia automáticamente al abrir Termux
```

### Desarrollo/Debug - Monitoreo Avanzado

```bash
# Ver estado detallado
blackbox-service status

# Monitorear logs en tiempo real
blackbox-service logs

# ✅ Información completa del sistema
# ✅ Logs en tiempo real para debugging
```

## 🔄 Integración con Comandos Existentes

### Alias Automáticos

El script de instalación crea automáticamente estos alias:

```bash
# Alias para interfaz web y servicios
alias llm-ui='blackbox-ui'
alias llm-service='blackbox-service'
alias llm-start='blackbox-service start'
alias llm-stop='blackbox-service stop'
alias llm-restart='blackbox-service restart'
alias llm-logs='blackbox-service logs'
```

### Comandos Rápidos

```bash
# Comandos súper cortos para uso diario
llm-ui                    # Abrir interfaz web
llm-start                 # Iniciar servicio
llm-stop                  # Detener servicio
llm-logs                  # Ver logs
```

## 🛡️ Características de Seguridad y Robustez

### Manejo de Errores

- ✅ **Verificación de dependencias** antes de iniciar
- ✅ **Validación de archivos** del proyecto
- ✅ **Manejo graceful** de señales de terminación
- ✅ **Limpieza automática** de archivos PID huérfanos
- ✅ **Timeouts configurables** para evitar procesos colgados

### Recuperación Automática

- ✅ **Monitor inteligente** que detecta caídas del servicio
- ✅ **Reinicio automático** con límites configurables
- ✅ **Logging detallado** de todos los eventos
- ✅ **Configuración persistente** que sobrevive reinicios

### Optimizaciones para Termux

- ✅ **Detección automática** del entorno Termux
- ✅ **Paths optimizados** para el sistema de archivos de Android
- ✅ **Configuración de red** adaptada para móviles
- ✅ **Gestión de batería** (debug off en producción)

## 📊 Comparación con Comandos Anteriores

| Aspecto | llm-web | blackbox-ui | blackbox-service |
|---------|---------|-------------|------------------|
| **Apertura de navegador** | Manual | ✅ Automática | ✅ Automática |
| **Persistencia** | ❌ Se cierra con Termux | ❌ Se cierra con Termux | ✅ Persiste |
| **Auto-reinicio** | ❌ No | ❌ No | ✅ Sí |
| **Monitoreo** | ❌ No | ❌ No | ✅ Completo |
| **Configuración** | ❌ Básica | ✅ Optimizada | ✅ Avanzada |
| **Logs** | ❌ Solo consola | ✅ Archivo | ✅ Gestión completa |
| **Estado** | ❌ No disponible | ✅ Básico | ✅ Detallado |

## 🚀 Flujo de Trabajo Recomendado

### Para Usuarios Casuales

1. **Instalación**: `./install_termux.sh`
2. **Configuración**: `llm-setup`
3. **Uso**: `blackbox-ui` (¡y listo!)

### Para Usuarios Avanzados

1. **Instalación**: `./install_termux.sh`
2. **Configuración**: `llm-setup`
3. **Servicio persistente**: `blackbox-service start`
4. **Monitor automático**: `blackbox-service monitor-start`
5. **Auto-inicio**: `blackbox-service setup-autostart`
6. **Monitoreo**: `blackbox-service status` y `blackbox-service logs`

## 🎉 Beneficios Principales

### ⚡ Productividad

- **Acceso instantáneo**: Un comando y tienes la interfaz web lista
- **Persistencia**: El servicio sigue funcionando aunque cierres Termux
- **Auto-recuperación**: Se reinicia automáticamente si algo falla

### 📱 Optimización Móvil

- **Navegador automático**: Se abre automáticamente en tu navegador móvil
- **Configuración optimizada**: Timeouts y configuración adaptada para móviles
- **Gestión de batería**: Configuración de producción para ahorrar batería

### 🔧 Facilidad de Uso

- **Comandos intuitivos**: `blackbox-ui` para interfaz, `blackbox-service` para gestión
- **Alias cortos**: `llm-ui`, `llm-start`, `llm-stop`, etc.
- **Ayuda integrada**: `--help` en todos los comandos

### 🛡️ Robustez

- **Monitor automático**: Detecta y corrige problemas automáticamente
- **Logging completo**: Registro detallado de todos los eventos
- **Configuración avanzada**: Control total sobre el comportamiento del servicio

---

## 🎯 Conclusión

Los nuevos comandos `blackbox-ui` y `blackbox-service` transforman completamente la experiencia de usar el CLI Universal para LLMs en Termux:

- **blackbox-ui**: Perfecto para uso casual con apertura automática del navegador
- **blackbox-service**: Ideal para uso productivo con servicio persistente y monitoreo

¡Ahora tienes acceso a LLMs desde tu móvil de manera profesional y robusta! 🚀📱