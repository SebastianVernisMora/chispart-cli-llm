te# Guía de Análisis de Directorios - Chispart CLI

## 🔍 Funcionalidades Implementadas

Esta guía describe las nuevas capacidades de análisis de directorios y codebase integradas en Chispart CLI v3.0.

### Características Principales

- **Análisis Estructural Completo**: Examina la estructura de archivos, dependencias, y patrones de proyecto
- **Análisis IA Integrado**: Utiliza modelos de IA para proporcionar insights y recomendaciones
- **Navegador Interactivo**: Interfaz de línea de comandos para explorar directorios
- **Comandos Especializados**: Análisis enfocado en arquitectura, seguridad, rendimiento, etc.
- **Integración con Chat**: Comandos especiales disponibles en modo interactivo

## 📋 Comandos CLI Disponibles

### 1. Análisis Completo de Directorio

```bash
chispart-dev analizar-directorio <directorio> [opciones]
```

**Opciones:**
- `--prompt, -p`: Prompt personalizado para el análisis IA
- `--modelo, -m`: Modelo específico a utilizar
- `--api, -a`: API específica a usar
- `--profundidad, --depth`: Profundidad máxima de análisis
- `--incluir-ocultos`: Incluir archivos y directorios ocultos
- `--sin-contenido`: No analizar contenido de archivos

**Ejemplos:**
```bash
# Análisis básico
chispart-dev analizar-directorio ./mi-proyecto

# Análisis profundo con configuración específica
chispart-dev analizar-directorio /home/user/codigo --profundidad 5 --modelo gpt-4

# Análisis con prompt personalizado
chispart-dev analizar-directorio . --prompt "Evalúa la seguridad del código"
```

### 2. Exploración Especializada de Código

```bash
chispart-dev explorar-codigo <directorio> [opciones]
```

**Enfoques disponibles:**
- `general`: Análisis general del codebase
- `architecture`: Enfoque en patrones arquitectónicos
- `security`: Análisis de seguridad
- `performance`: Optimización y rendimiento
- `testing`: Estrategias de testing

**Ejemplos:**
```bash
# Análisis de arquitectura
chispart-dev explorar-codigo ./proyecto --enfoque architecture

# Análisis de seguridad
chispart-dev explorar-codigo . --enfoque security --modelo gpt-4

# Análisis de rendimiento
chispart-dev explorar-codigo /path/to/code --enfoque performance
```

### 3. Análisis de Patrones de Proyecto

```bash
chispart-dev patrones-proyecto <directorio> [opciones]
```

Identifica patrones de diseño, arquitectura y mejores prácticas.

**Ejemplos:**
```bash
# Análisis de patrones
chispart-dev patrones-proyecto ./mi-app

# Con modelo específico
chispart-dev patrones-proyecto . --modelo claude-3.5-sonnet
```

### 4. Navegador Interactivo

```bash
chispart-dev navegador
```

Abre una interfaz interactiva para navegar y analizar directorios.

**Comandos del navegador:**
- `ls, dir` - Listar contenido
- `cd <directorio>` - Cambiar directorio
- `analizar` - Analizar directorio actual
- `tree [profundidad]` - Mostrar árbol de directorios
- `info` - Información detallada
- `bookmark [nombre]` - Guardar marcador
- `bookmarks` - Ver marcadores
- `back` - Volver atrás
- `help` - Mostrar ayuda

## 🗣️ Integración con Chat Interactivo

En el modo interactivo (`chispart-dev interactivo`), están disponibles comandos especiales:

### Comandos Especiales

```bash
# Analizar directorio desde el chat
@analizar <ruta>

# Explorar código con enfoque específico
@explorar <ruta> --enfoque <tipo>

# Abrir navegador de directorios
navegador

# Ver comandos disponibles
comandos
```

### Ejemplos en Chat Interactivo

```
Tú $ @analizar ./mi-proyecto
🔍 Analizando directorio: ./mi-proyecto
[Análisis estructural y respuesta IA integrada en la conversación]

Tú $ @explorar . --enfoque security
🔍 Explorando código en: . (enfoque: security)
[Análisis de seguridad integrado en la conversación]

Tú $ navegador
🗂️ Abriendo navegador de directorios...
[Interfaz interactiva de navegación]
```

## 🏗️ Arquitectura de la Implementación

### Módulos Principales

1. **`core/directory_analyzer.py`**
   - Clase `CodebaseAnalyzer`: Análisis estructural completo
   - Detección de tipos de proyecto y lenguajes
   - Análisis de dependencias y arquitectura
   - Generación de recomendaciones

2. **`commands/directory_commands.py`**
   - Clase `DirectoryCommands`: Manejo de comandos de directorio
   - Integración con IA para análisis avanzado
   - Validación y manejo de errores

3. **`ui/directory_browser.py`**
   - Clase `DirectoryBrowser`: Navegador interactivo
   - Comandos de navegación y análisis
   - Sistema de marcadores y cache

4. **`core/command_handler.py`** (extendido)
   - Métodos de manejo de análisis de directorios
   - Integración con el sistema existente
   - Estadísticas y logging

### Flujo de Análisis

1. **Validación**: Verificar permisos y existencia del directorio
2. **Análisis Estructural**: Examinar archivos, dependencias, patrones
3. **Procesamiento IA**: Enviar datos estructurados a la IA
4. **Presentación**: Mostrar resultados formateados
5. **Persistencia**: Guardar en historial de conversaciones

## 🔧 Configuración y Personalización

### Variables de Entorno

Las mismas variables de API que usa Chispart CLI:
- `CHISPART_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- etc.

### Personalización de Análisis

- **Profundidad**: Controla qué tan profundo analizar la estructura
- **Filtros**: Incluir/excluir archivos ocultos
- **Enfoques**: Especializar el análisis según necesidades
- **Modelos**: Elegir el modelo de IA más apropiado

## 📊 Tipos de Análisis Proporcionados

### Análisis Estructural
- Conteo de archivos y directorios
- Detección de lenguajes de programación
- Identificación de tipos de archivo
- Análisis de tamaños y distribución

### Análisis de Proyecto
- Detección automática del tipo de proyecto
- Identificación de gestores de paquetes
- Análisis de dependencias
- Patrones de arquitectura detectados

### Análisis IA
- Evaluación de calidad del código
- Recomendaciones de mejores prácticas
- Identificación de problemas potenciales
- Sugerencias de optimización

### Análisis Especializado
- **Arquitectura**: Patrones de diseño, escalabilidad
- **Seguridad**: Vulnerabilidades, configuraciones
- **Rendimiento**: Optimizaciones, bottlenecks
- **Testing**: Cobertura, estrategias

## 🚀 Casos de Uso

### Para Desarrolladores
- Evaluar proyectos nuevos o heredados
- Identificar áreas de mejora
- Documentar arquitectura existente
- Auditorías de código

### Para Equipos
- Revisiones de código estructuradas
- Establecer estándares de proyecto
- Onboarding de nuevos miembros
- Análisis de deuda técnica

### Para Arquitectos
- Evaluación de patrones arquitectónicos
- Identificación de anti-patrones
- Planificación de refactoring
- Análisis de escalabilidad

## 🔍 Ejemplos Prácticos

### Análisis de Proyecto React

```bash
# Análisis completo
chispart-dev analizar-directorio ./my-react-app

# Enfoque en arquitectura frontend
chispart-dev explorar-codigo ./my-react-app --enfoque architecture

# Análisis de rendimiento
chispart-dev explorar-codigo ./my-react-app --enfoque performance
```

### Análisis de API Backend

```bash
# Análisis de seguridad
chispart-dev explorar-codigo ./api-backend --enfoque security

# Patrones de arquitectura
chispart-dev patrones-proyecto ./api-backend

# Navegación interactiva
chispart-dev navegador
# Luego: cd ./api-backend && analizar
```

### Integración en Workflow

```bash
# En modo interactivo
chispart-dev interactivo

# Dentro del chat:
Tú $ @analizar ./proyecto
Tú $ Basándote en el análisis, ¿qué mejoras recomiendas?
Tú $ @explorar ./src --enfoque security
Tú $ ¿Hay vulnerabilidades críticas que deba atender?
```

## 🛠️ Troubleshooting

### Problemas Comunes

1. **Error de permisos**: Verificar permisos de lectura del directorio
2. **Directorio muy grande**: Usar `--profundidad` para limitar análisis
3. **Memoria insuficiente**: Usar `--sin-contenido` para análisis más ligero
4. **API no responde**: Verificar configuración de claves API

### Optimización

- Para proyectos grandes, usar profundidad limitada (3-5 niveles)
- Excluir directorios innecesarios (node_modules, .git, etc.)
- Usar cache del navegador para análisis repetidos
- Elegir modelos apropiados según complejidad

## 📈 Próximas Mejoras

- Análisis de métricas de código (complejidad ciclomática, etc.)
- Integración con herramientas de análisis estático
- Exportación de reportes en múltiples formatos
- Análisis comparativo entre versiones
- Integración con sistemas de CI/CD

---

**Nota**: Esta funcionalidad está integrada en Chispart CLI v3.0 y requiere una clave API válida para el análisis IA.
