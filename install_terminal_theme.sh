#!/bin/bash

# Script para instalar el tema personalizado de la terminal

# Contenido del tema de Oh My Posh (aliens.omp.json)
THEME_JSON='''
{
  "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json",
  "upgrade": {
    "source": "cdn",
    "interval": "168h",
    "auto": false,
    "notice": false
  },
  "blocks": [
    {
      "type": "prompt",
      "alignment": "left",
      "segments": [
        {
          "leading_diamond": "\ue0b6",
          "trailing_diamond": "\ue0b0",
          "template": " {{ .UserName }}@{{ .HostName }} ",
          "foreground": "#ffffff",
          "background": "#61AFEF",
          "type": "session",
          "style": "diamond"
        },
        {
          "properties": {
            "style": "full"
          },
          "template": " {{ .Path }} ",
          "foreground": "#ffffff",
          "powerline_symbol": "\ue0b0",
          "background": "#C678DD",
          "type": "path",
          "style": "powerline"
        },
        {
          "template": " {{ .HEAD }} ",
          "foreground": "#193549",
          "powerline_symbol": "\ue0b0",
          "background": "#95ffa4",
          "type": "git",
          "style": "powerline"
        },
        {
          "leading_diamond": "<transparent,background>\ue0b0</>",
          "trailing_diamond": "\ue0b4",
          "template": " {{ if .Error }}{{ .Error }}{{ else }}{{ if .Venv }}{{ .Venv }} {{ end }}{{ .Full }}{{ end }} ",
          "foreground": "#ffffff",
          "background": "#FF6471",
          "type": "python",
          "style": "diamond"
        }
      ]
    },
    {
      "type": "prompt",
      "alignment": "right",
      "segments": [
        {
          "type": "time",
          "style": "diamond",
          "leading_diamond": "\ue0b6",
          "trailing_diamond": "\ue0b4",
          "foreground": "#212121",
          "background": "#64B5F6",
          "properties": {
            "time_format": "15:04:05",
            "cache_duration": "none"
          },
          "template": " \uf017 {{ .CurrentDate | date .Format }} "
        }
      ]
    },
    {
      "type": "prompt",
      "alignment": "left",
      "newline": true,
      "segments": [
        {
          "type": "text",
          "style": "plain",
          "foreground_templates": [
            "{{ if gt .Code 0 }}#FF3131{{ end }}",
            "{{ else }}#39FF14{{ end }}"
          ],
          "template": "❯"
        }
      ]
    }
  ],
  "version": 3,
  "final_space": true
}
'''

# Ruta del archivo de tema en el directorio home
THEME_PATH="$HOME/aliens.omp.json"

# Escribir el contenido del tema en el archivo
echo "$THEME_JSON" > "$THEME_PATH"

# --- Configuración para .bashrc ---
BASHRC_CONFIG='''

# --- Configuración del Tema de Terminal Personalizado ---

# 1. Configuración del prompt de Oh My Posh
PROMPT_COMMAND='PS1="$(oh-my-posh print primary --config ~/aliens.omp.json --shell bash)"'

# 2. Banner dinámico
function draw_banner() {
    # Limpia la pantalla y dibuja el banner
    # Nota: La ruta a oh-my-logo puede variar. Este script asume que está en el PATH.
    # Si no funciona, se necesita la ruta absoluta.
    if command -v oh-my-logo &> /dev/null; then
        oh-my-logo "Chispart CLI" --filled nebula --letter-spacing 0.1
    else
        echo "Advertencia: El comando 'oh-my-logo' no se encontró. El banner no se mostrará."
    fi
}

# Atrapa el cambio de tamaño de la ventana para redibujar el banner
trap draw_banner WINCH

# Dibuja el banner en la carga inicial
draw_banner

# --- Fin de la Configuración del Tema ---
'''

# Añadir la configuración a .bashrc si no existe
if ! grep -q "# --- Configuración del Tema de Terminal Personalizado ---" "$HOME/.bashrc"; then
    echo "$BASHRC_CONFIG" >> "$HOME/.bashrc"
    echo "¡Tema instalado! Por favor, reinicia tu terminal o ejecuta 'source ~/.bashrc'."
else
    echo "El tema ya parece estar instalado. No se realizaron cambios en .bashrc."
fi

