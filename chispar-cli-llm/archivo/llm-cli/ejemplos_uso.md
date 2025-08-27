# 📖 Ejemplos de Uso - CLI Universal para LLMs

## 🚀 Comandos Básicos

### Ver ayuda general
```bash
python blackbox_cli.py --help
```

### Ver APIs disponibles
```bash
python blackbox_cli.py --help
# Muestra: [blackbox|openai|anthropic|groq|together]
```

## 🤖 Selección de API

### BlackboxAI (por defecto)
```bash
python blackbox_cli.py chat "Hola mundo"
# o explícitamente:
python blackbox_cli.py --api blackbox chat "Hola mundo"
```

### OpenAI
```bash
python blackbox_cli.py --api openai chat "Hola mundo"
```

### Anthropic Claude
```bash
python blackbox_cli.py --api anthropic chat "Hola mundo"
```

### Groq
```bash
python blackbox_cli.py --api groq chat "Hola mundo"
```

### Together AI
```bash
python blackbox_cli.py --api together chat "Hola mundo"
```

## 📋 Ver Modelos Disponibles

### Por API
```bash
# BlackboxAI
python blackbox_cli.py --api blackbox modelos

# OpenAI
python blackbox_cli.py --api openai modelos

# Anthropic
python blackbox_cli.py --api anthropic modelos

# Groq
python blackbox_cli.py --api groq modelos

# Together AI
python blackbox_cli.py --api together modelos
```

## 💬 Chat con Modelos Específicos

### BlackboxAI
```bash
# GPT-4
python blackbox_cli.py --api blackbox chat "Explica la fotosíntesis" --modelo gpt-4

# Claude 3 Sonnet
python blackbox_cli.py --api blackbox chat "Explica la fotosíntesis" --modelo claude-3-sonnet

# Llama 3.1 70B
python blackbox_cli.py --api blackbox chat "Explica la fotosíntesis" --modelo llama-3.1-70b

# Mixtral 8x7B
python blackbox_cli.py --api blackbox chat "Explica la fotosíntesis" --modelo mixtral-8x7b
```

### OpenAI (requiere OPENAI_API_KEY)
```bash
# GPT-4
python blackbox_cli.py --api openai chat "Explica la fotosíntesis" --modelo gpt-4

# GPT-4 Turbo
python blackbox_cli.py --api openai chat "Explica la fotosíntesis" --modelo gpt-4-turbo

# GPT-3.5 Turbo
python blackbox_cli.py --api openai chat "Explica la fotosíntesis" --modelo gpt-3.5-turbo
```

### Anthropic (requiere ANTHROPIC_API_KEY)
```bash
# Claude 3 Opus
python blackbox_cli.py --api anthropic chat "Explica la fotosíntesis" --modelo claude-3-opus

# Claude 3 Sonnet
python blackbox_cli.py --api anthropic chat "Explica la fotosíntesis" --modelo claude-3-sonnet

# Claude 3 Haiku
python blackbox_cli.py --api anthropic chat "Explica la fotosíntesis" --modelo claude-3-haiku
```

## 🖼️ Análisis de Imágenes

### APIs que soportan imágenes: blackbox, openai, anthropic

```bash
# BlackboxAI con GPT-4 Vision
python blackbox_cli.py --api blackbox imagen foto.jpg --modelo gpt-4-vision

# OpenAI con GPT-4 Vision
python blackbox_cli.py --api openai imagen foto.jpg --modelo gpt-4-vision

# Con prompt personalizado
python blackbox_cli.py --api blackbox imagen foto.jpg --prompt "¿Qué colores predominan en esta imagen?"
```

## 📄 Análisis de PDFs

### APIs que soportan PDFs: blackbox, openai

```bash
# BlackboxAI
python blackbox_cli.py --api blackbox pdf documento.pdf

# OpenAI
python blackbox_cli.py --api openai pdf documento.pdf

# Con prompt personalizado
python blackbox_cli.py --api blackbox pdf informe.pdf --prompt "¿Cuáles son las conclusiones principales?"
```

## 🔄 Modo Interactivo

### Con diferentes APIs
```bash
# BlackboxAI
python blackbox_cli.py --api blackbox interactivo

# OpenAI
python blackbox_cli.py --api openai interactivo --modelo gpt-4

# Anthropic
python blackbox_cli.py --api anthropic interactivo --modelo claude-3-sonnet

# Groq
python blackbox_cli.py --api groq interactivo --modelo llama-3.1-70b
```

## 📊 Historial

```bash
# Ver historial (todas las APIs)
python blackbox_cli.py historial

# Ver últimas 5 conversaciones
python blackbox_cli.py historial --limite 5
```

## 🔧 Configuración de Variables de Entorno

### Archivo .env
```bash
# Crear archivo .env
cp .env.example .env

# Editar .env
BLACKBOX_API_KEY=sk-sh9bLJVy1zBZiwc5yuJoGA
OPENAI_API_KEY=tu_clave_openai
ANTHROPIC_API_KEY=tu_clave_anthropic
GROQ_API_KEY=tu_clave_groq
TOGETHER_API_KEY=tu_clave_together
```

### Exportar en terminal
```bash
export OPENAI_API_KEY="tu_clave_openai"
export ANTHROPIC_API_KEY="tu_clave_anthropic"
export GROQ_API_KEY="tu_clave_groq"
export TOGETHER_API_KEY="tu_clave_together"
```

## 🎯 Casos de Uso Prácticos

### Comparar respuestas entre APIs
```bash
# Misma pregunta a diferentes APIs
python blackbox_cli.py --api blackbox chat "¿Cuál es la diferencia entre Python y JavaScript?"
python blackbox_cli.py --api openai chat "¿Cuál es la diferencia entre Python y JavaScript?"
python blackbox_cli.py --api anthropic chat "¿Cuál es la diferencia entre Python y JavaScript?"
```

### Análisis de código
```bash
python blackbox_cli.py --api blackbox chat "Explica este código: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
```

### Traducción
```bash
python blackbox_cli.py --api anthropic chat "Traduce al inglés: 'La inteligencia artificial está transformando el mundo'"
```

### Análisis de imagen técnica
```bash
python blackbox_cli.py --api openai imagen diagrama.png --prompt "Explica este diagrama técnico paso a paso"
```

### Resumen de documento
```bash
python blackbox_cli.py --api blackbox pdf contrato.pdf --prompt "Resume los puntos más importantes de este contrato"
```

## ⚠️ Notas Importantes

1. **BlackboxAI** ya está configurada y lista para usar
2. **Otras APIs** requieren configurar sus respectivas claves API
3. **Análisis de imágenes** solo funciona con: blackbox, openai, anthropic
4. **Análisis de PDFs** solo funciona con: blackbox, openai
5. **Límite de archivos**: 20MB máximo
6. **Formatos soportados**: 
   - Imágenes: JPG, JPEG, PNG, WebP
   - Documentos: PDF
