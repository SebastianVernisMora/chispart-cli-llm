# 🚀 Guía de Activación: Blackbox-Copilot Integration

## ✅ Estado Actual
La extensión **YA ESTÁ INSTALADA**: `blackbox-integration.blackbox-copilot-integration`

## 🔧 Cómo Ver y Usar la Extensión

### **1. Verificar en VSCode Extensions**
1. Abre VSCode
2. Ve a **Extensions** (Ctrl+Shift+X)
3. Busca "Blackbox" o "blackbox-copilot-integration"
4. Debería aparecer como **instalada** y **habilitada**

### **2. Activar los Comandos**
Abre **Command Palette** (Ctrl+Shift+P) y busca:

- ✅ `Blackbox: Toggle Integration`
- ✅ `Blackbox: Configure API Key` 
- ✅ `Blackbox: Analyze Code with Blackbox`
- ✅ `Blackbox: Enhance Copilot with Blackbox`

### **3. Usar Keybindings**
- **Ctrl+Alt+B**: Toggle Integration
- **Ctrl+Shift+B**: Analyze Code

### **4. Configurar API Key**
1. Command Palette → `Blackbox: Configure API Key`
2. Ingresa tu API Key de [blackbox.ai](https://blackbox.ai)
3. La extensión se activará automáticamente

## 🔍 Si No La Ves

### **Opción A: Reiniciar VSCode**
```bash
# Cerrar VSCode completamente y reabrir
code --new-window
```

### **Opción B: Verificar Estado**
```bash
# Ver todas las extensiones instaladas
code --list-extensions

# Verificar que esté habilitada
code --list-extensions --show-versions | grep blackbox
```

### **Opción C: Forzar Recarga**
1. En VSCode: **Developer** → **Reload Window**
2. O usa Ctrl+Shift+P → "Developer: Reload Window"

## 🎯 Cómo Funciona

### **Integración Automática**
- Al escribir código, las sugerencias ahora incluyen **Blackbox AI**
- Las sugerencias aparecen marcadas como "Blackbox AI"
- Se combina con GitHub Copilot automáticamente

### **Análisis de Código**
- Selecciona código → Click derecho → "Analyze Code with Blackbox"
- O usa Ctrl+Shift+B

### **Configuraciones Disponibles**
Ve a **Settings** → busca "Blackbox":
- API Key
- Endpoint
- Max Tokens
- Temperature
- Priority vs Copilot

## 🐛 Troubleshooting

### **No aparecen comandos**
- Verifica que GitHub Copilot esté instalado
- Reinicia VSCode completamente

### **No funciona la integración**
- Configura la API Key primero
- Verifica conexión a internet
- Revisa Developer Console (F12) para errores

### **Sugerencias no aparecen**
- Asegúrate de tener API Key válida
- Verifica que esté habilitada en Settings
- Prueba en archivos .js, .py, .ts

## ✨ ¡La extensión está lista para usar!

Solo necesitas:
1. **Configurar API Key** de Blackbox
2. **Reiniciar VSCode** si es necesario
3. **Empezar a escribir código** y ver las sugerencias mejoradas
