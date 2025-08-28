# 📊 Sistema de Logging - CLI Universal para LLMs

## 🎯 Descripción General

Este documento describe el sistema de logging implementado para la aplicación CLI Universal para LLMs, siguiendo las mejores prácticas de la industria para observabilidad, monitoreo y auditoría.

## 🏗️ Arquitectura del Sistema de Logging

### Componentes Principales

1. **`logger_config.py`** - Configuración central del sistema de logging
2. **`LoggerMixin`** - Clase base para agregar capacidades de logging
3. **Formateadores especializados** - Para diferentes tipos de salida
4. **Handlers múltiples** - Para diferentes destinos de logs

## 📋 Características Implementadas

### ✅ Logging Estructurado
- **Formato JSON** para logs de archivo (facilita análisis automatizado)
- **Formato colorizado** para consola (mejor experiencia de desarrollo)
- **Metadatos enriquecidos** con contexto de la aplicación

### ✅ Rotación de Archivos
- **Tamaño máximo**: 10MB por archivo
- **Archivos de backup**: 5 archivos históricos
- **Limpieza automática** de archivos antiguos

### ✅ Niveles de Logging Diferenciados
- **DEBUG**: Información detallada para desarrollo
- **INFO**: Eventos normales de la aplicación
- **WARNING**: Situaciones que requieren atención
- **ERROR**: Errores que no detienen la aplicación
- **CRITICAL**: Errores graves que pueden detener la aplicación

### ✅ Separación por Tipo de Log
- **Archivo principal** (`llm_cli.log`): Todos los eventos
- **Archivo de errores** (`llm_cli_errors.log`): Solo errores y críticos
- **Archivo de auditoría** (`llm_cli_audit.log`): Eventos de auditoría y métricas

## 🔧 Configuración

### Variables de Entorno Soportadas

```bash
# Nivel de logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Directorio de logs
LOG_DIR=logs

# Configuración avanzada (opcional)
LOG_MAX_FILE_SIZE=10485760  # 10MB en bytes
LOG_BACKUP_COUNT=5
LOG_ENABLE_CONSOLE=true
LOG_ENABLE_FILE=true
LOG_STRUCTURED_FORMAT=true
```

### Inicialización Automática

```python
from logger_config import get_logger, LoggerMixin

# Obtener logger específico
logger = get_logger('mi_modulo')

# O usar el mixin en una clase
class MiClase(LoggerMixin):
    def mi_metodo(self):
        self.logger.info("Método ejecutado")
```

## 📊 Tipos de Logs Generados

### 1. Logs de Aplicación General

```json
{
  "timestamp": "2025-01-22T10:30:45.123Z",
  "level": "INFO",
  "logger": "llm_cli.flask_app",
  "message": "Application started successfully",
  "module": "app",
  "function": "main",
  "line": 245
}
```

### 2. Logs de Llamadas a API

```json
{
  "timestamp": "2025-01-22T10:31:15.456Z",
  "level": "INFO",
  "logger": "llm_cli.WebAppLogger",
  "message": "API call completed: blackbox/gpt-4",
  "api_name": "blackbox",
  "model_name": "gpt-4",
  "execution_time": 1250.5,
  "tokens_used": 150,
  "request_id": "req_abc123",
  "audit": true
}
```

### 3. Logs de Acciones de Usuario

```json
{
  "timestamp": "2025-01-22T10:31:00.789Z",
  "level": "INFO",
  "logger": "llm_cli.CLILogger",
  "message": "User action: chat_command_executed",
  "user_id": "user_123",
  "session_id": "sess_456",
  "api_name": "blackbox",
  "model_name": "gpt-4",
  "message_length": 45,
  "audit": true
}
```

### 4. Logs de Errores

```json
{
  "timestamp": "2025-01-22T10:32:30.012Z",
  "level": "ERROR",
  "logger": "llm_cli.WebAppLogger",
  "message": "Error occurred: API rate limit exceeded",
  "error_code": "API_429",
  "request_id": "req_def456",
  "api_name": "openai",
  "exception": {
    "type": "APIError",
    "message": "Rate limit exceeded",
    "traceback": "..."
  }
}
```

## 🎨 Formatos de Salida

### Consola (Desarrollo)
```
[2025-01-22 10:30:45] INFO llm_cli.flask_app - Application started [api=blackbox, model=gpt-4, time=1250ms]
```

### Archivo JSON (Producción)
```json
{"timestamp": "2025-01-22T10:30:45.123Z", "level": "INFO", "message": "Application started", ...}
```

## 🔍 Métricas y Auditoría

### Métricas Automáticas Capturadas

1. **Rendimiento**
   - Tiempo de ejecución de llamadas API
   - Tiempo de respuesta de endpoints web
   - Latencia de procesamiento de archivos

2. **Uso de Recursos**
   - Tokens consumidos por API
   - Tamaño de archivos procesados
   - Número de requests por sesión

3. **Actividad de Usuario**
   - Comandos ejecutados
   - APIs utilizadas
   - Modelos seleccionados
   - Sesiones interactivas

### Eventos de Auditoría

- Inicio/fin de aplicación
- Cambios de configuración
- Errores de autenticación
- Acceso a archivos sensibles
- Llamadas a APIs externas

## 📈 Análisis y Monitoreo

### Consultas Útiles para Análisis

```bash
# Errores en las últimas 24 horas
grep '"level":"ERROR"' logs/llm_cli.log | grep $(date -d "1 day ago" +%Y-%m-%d)

# APIs más utilizadas
grep '"audit":true' logs/llm_cli_audit.log | jq -r '.api_name' | sort | uniq -c | sort -nr

# Tiempo promedio de respuesta por modelo
grep '"execution_time"' logs/llm_cli_audit.log | jq -r '"\(.model_name) \(.execution_time)"' | awk '{sum[$1]+=$2; count[$1]++} END {for(i in sum) print i, sum[i]/count[i]}'

# Tokens consumidos por día
grep '"tokens_used"' logs/llm_cli_audit.log | jq -r '"\(.timestamp[:10]) \(.tokens_used)"' | awk '{sum[$1]+=$2} END {for(i in sum) print i, sum[i]}'
```

### Integración con Herramientas de Monitoreo

El formato JSON estructurado permite fácil integración con:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana + Loki**
- **Splunk**
- **DataDog**
- **New Relic**

## 🛠️ Uso en el Código

### CLI Application

```python
from logger_config import get_logger, LoggerMixin

class CLILogger(LoggerMixin):
    pass

cli_logger = CLILogger()

# Logging de comandos
cli_logger.log_user_action(
    "chat_command_executed",
    request_id=request_id,
    api_name=api_name,
    model_name=modelo
)

# Logging de llamadas API
cli_logger.log_api_call(
    api_name=api_name,
    model_name=modelo,
    execution_time=execution_time,
    tokens_used=tokens_used,
    request_id=request_id
)

# Logging de errores
cli_logger.log_error(
    exception,
    context={'request_id': request_id, 'api_name': api_name}
)
```

### Web Application

```python
from logger_config import get_logger, LoggerMixin

class WebAppLogger(LoggerMixin):
    pass

web_logger = WebAppLogger()

# Decorador para logging automático
@log_request
def my_endpoint():
    # El decorador automáticamente logea request/response
    pass

# Logging manual
web_logger.logger.info(
    "Processing user request",
    extra={
        'request_id': request_id,
        'user_id': user_id,
        'endpoint': '/api/chat'
    }
)
```

## 🔒 Seguridad y Privacidad

### Datos Sensibles Excluidos

- **Claves API**: Nunca se logean las claves completas
- **Contenido de mensajes**: Solo se logea la longitud, no el contenido
- **Información personal**: Se evita loggear datos identificables

### Rotación y Retención

- **Rotación automática**: Cada 10MB
- **Retención**: 5 archivos de backup (≈50MB total)
- **Limpieza**: Archivos antiguos se eliminan automáticamente

## 📚 Mejores Prácticas Implementadas

### ✅ Logging Estructurado
- Formato JSON consistente
- Campos estandarizados
- Metadatos enriquecidos

### ✅ Separación de Responsabilidades
- Logs de aplicación vs auditoría
- Diferentes niveles por tipo de evento
- Handlers especializados

### ✅ Rendimiento Optimizado
- Logging asíncrono donde es posible
- Rotación eficiente de archivos
- Filtros para evitar spam de logs

### ✅ Observabilidad Completa
- Trazabilidad con request IDs
- Métricas de rendimiento
- Contexto de errores detallado

### ✅ Configurabilidad
- Variables de entorno
- Niveles ajustables
- Formatos intercambiables

## 🚀 Beneficios del Sistema

1. **Debugging Eficiente**: Logs detallados con contexto completo
2. **Monitoreo Proactivo**: Métricas automáticas de rendimiento
3. **Auditoría Completa**: Trazabilidad de todas las acciones
4. **Análisis de Uso**: Estadísticas de APIs y modelos utilizados
5. **Detección de Problemas**: Alertas automáticas basadas en logs
6. **Optimización**: Datos para mejorar rendimiento y experiencia

## 📋 Checklist de Implementación

- ✅ **Configuración centralizada** en `logger_config.py`
- ✅ **Formateadores especializados** (JSON + Consola colorizada)
- ✅ **Rotación automática** de archivos de log
- ✅ **Separación por tipo** (app, errores, auditoría)
- ✅ **Logging estructurado** con metadatos enriquecidos
- ✅ **Mixin reutilizable** para todas las clases
- ✅ **Decoradores automáticos** para web requests
- ✅ **Métricas de rendimiento** integradas
- ✅ **Trazabilidad completa** con request IDs
- ✅ **Manejo seguro** de datos sensibles
- ✅ **Configuración por variables** de entorno
- ✅ **Documentación completa** y ejemplos de uso

Este sistema de logging proporciona una base sólida para el monitoreo, debugging y análisis de la aplicación CLI Universal para LLMs, siguiendo las mejores prácticas de la industria.
