#!/usr/bin/env python3
"""
Script de migración de Chispart CLI Legacy a Chispart CLI Modern
Migra configuraciones, historial y preferencias del usuario
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from ui.components import console, create_panel
from ui.theme_manager import get_theme

def backup_legacy_files():
    """Crea backup de archivos importantes del sistema legacy"""
    backup_dir = Path("backup_legacy")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        ".env",
        "chat_history.json",
        "config.json",
        "user_preferences.json"
    ]
    
    backed_up = []
    for file_name in files_to_backup:
        file_path = Path(file_name)
        if file_path.exists():
            backup_path = backup_dir / file_name
            shutil.copy2(file_path, backup_path)
            backed_up.append(file_name)
    
    return backed_up, backup_dir

def migrate_env_file() -> Dict[str, str]:
    """Migra variables de entorno del archivo .env legacy"""
    env_vars = {}
    env_file = Path(".env")
    
    if not env_file.exists():
        return env_vars
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Limpiar comillas
                    value = value.strip().strip('"').strip("'")
                    env_vars[key.strip()] = value
        
        console.print(f"[green]✅ Migradas {len(env_vars)} variables de entorno[/green]")
        
    except Exception as e:
        console.print(f"[yellow]⚠️ Error migrando .env: {e}[/yellow]")
    
    return env_vars

def migrate_chat_history() -> int:
    """Migra el historial de chat del formato legacy"""
    history_file = Path("chat_history.json")
    migrated_count = 0
    
    if not history_file.exists():
        return migrated_count
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            legacy_history = json.load(f)
        
        # El formato legacy ya es compatible, solo verificamos estructura
        if isinstance(legacy_history, list):
            migrated_count = len(legacy_history)
            console.print(f"[green]✅ Historial compatible: {migrated_count} conversaciones[/green]")
        else:
            console.print("[yellow]⚠️ Formato de historial no reconocido[/yellow]")
            
    except Exception as e:
        console.print(f"[yellow]⚠️ Error migrando historial: {e}[/yellow]")
    
    return migrated_count

def create_modern_config(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Crea configuración moderna basada en variables legacy"""
    
    # Mapeo de variables legacy a modernas
    api_key_mapping = {
        'OPENAI_API_KEY': 'openai',
        'ANTHROPIC_API_KEY': 'anthropic', 
        'GROQ_API_KEY': 'groq',
        'TOGETHER_API_KEY': 'together',
        'BLACKBOX_API_KEY': 'chispart',
        'CHISPART_API_KEY': 'chispart'
    }
    
    modern_config = {
        "version": "2.0.0",
        "configured_apis": [],
        "current_api": "chispart",
        "current_theme": "neon",
        "user_preferences": {
            "save_history": True,
            "stream_responses": False,
            "show_tokens": True,
            "auto_detect_termux": True
        },
        "migration": {
            "from_legacy": True,
            "migration_date": None
        }
    }
    
    # Detectar APIs configuradas
    for env_key, api_name in api_key_mapping.items():
        if env_key in env_vars and env_vars[env_key]:
            modern_config["configured_apis"].append(api_name)
    
    # Establecer API por defecto basada en lo que esté configurado
    if modern_config["configured_apis"]:
        if "chispart" in modern_config["configured_apis"]:
            modern_config["current_api"] = "chispart"
        elif "openai" in modern_config["configured_apis"]:
            modern_config["current_api"] = "openai"
        else:
            modern_config["current_api"] = modern_config["configured_apis"][0]
    
    return modern_config

def save_modern_config(config: Dict[str, Any]):
    """Guarda la configuración moderna"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "chispart_config.json"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✅ Configuración moderna guardada en {config_file}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error guardando configuración: {e}[/red]")
        return False

def update_scripts():
    """Actualiza scripts de ejecución para usar la versión moderna"""
    
    scripts_to_update = {
        "chispart": "chispart_cli_modern.py",
        "chispart-ui": "app.py",  # Mantener la interfaz web
        "chs": "chispart_cli_modern.py"
    }
    
    updated_scripts = []
    
    for script_name, target_file in scripts_to_update.items():
        script_path = Path(script_name)
        
        if script_path.exists():
            # Crear backup del script original
            backup_path = Path(f"backup_legacy/{script_name}.backup")
            backup_path.parent.mkdir(exist_ok=True)
            shutil.copy2(script_path, backup_path)
            
            # Actualizar script para usar versión moderna
            script_content = f"""#!/bin/bash
# Chispart CLI Modern - Script actualizado automáticamente
# Backup del original en: backup_legacy/{script_name}.backup

cd "$(dirname "$0")"
python3 {target_file} "$@"
"""
            
            try:
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                # Hacer ejecutable
                os.chmod(script_path, 0o755)
                updated_scripts.append(script_name)
                
            except Exception as e:
                console.print(f"[yellow]⚠️ Error actualizando {script_name}: {e}[/yellow]")
    
    if updated_scripts:
        console.print(f"[green]✅ Scripts actualizados: {', '.join(updated_scripts)}[/green]")
    
    return updated_scripts

def show_migration_summary(backed_up_files, migrated_history_count, configured_apis, updated_scripts):
    """Muestra resumen de la migración"""
    
    colors = get_theme()
    
    summary = f"""
[{colors['primary']}]🚀 Migración Completada Exitosamente[/]

[{colors['secondary']}]📁 Archivos respaldados:[/]
{chr(10).join(f"[{colors['info']}]  • {file}[/]" for file in backed_up_files)}

[{colors['secondary']}]📚 Historial migrado:[/]
[{colors['info']}]  • {migrated_history_count} conversaciones preservadas[/]

[{colors['secondary']}]🔑 APIs configuradas:[/]
{chr(10).join(f"[{colors['success']}]  • {api}[/]" for api in configured_apis)}

[{colors['secondary']}]🔧 Scripts actualizados:[/]
{chr(10).join(f"[{colors['info']}]  • {script}[/]" for script in updated_scripts)}

[{colors['warning']}]📋 Próximos pasos:[/]
[{colors['dim']}]1. Ejecuta: ./chispart estado[/]
[{colors['dim']}]2. Verifica: ./chispart configurar[/]
[{colors['dim']}]3. Prueba: ./chispart chat "¡Hola desde la versión moderna!"[/]

[{colors['success']}]¡Tu instalación de Chispart CLI ha sido modernizada![/]
"""
    
    console.print(create_panel(
        summary,
        title="Resumen de Migración",
        style="chispart.brand"
    ))

def main():
    """Función principal de migración"""
    
    colors = get_theme()
    
    # Banner de migración
    console.print(create_panel(
        f"""
[{colors['primary']}]🔄 Migración a Chispart CLI Modern[/]

[{colors['dim']}]Este script migrará tu instalación legacy de Chispart CLI[/]
[{colors['dim']}]a la nueva arquitectura modular con mejoras de rendimiento[/]
[{colors['dim']}]y funcionalidades avanzadas.[/]

[{colors['warning']}]⚠️ Se crearán backups de todos los archivos importantes[/]
""",
        title="Asistente de Migración",
        style="chispart.brand"
    ))
    
    # Confirmar migración
    try:
        confirm = input(f"\n{colors['accent']}¿Proceder con la migración? (s/N): {colors['reset']}")
        if confirm.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
            console.print(f"[{colors['warning']}]Migración cancelada[/]")
            return
    except KeyboardInterrupt:
        console.print(f"\n[{colors['warning']}]Migración cancelada[/]")
        return
    
    console.print(f"\n[{colors['primary']}]🚀 Iniciando migración...[/]")
    
    # Paso 1: Backup
    console.print(f"[{colors['info']}]📁 Creando backups...[/]")
    backed_up_files, backup_dir = backup_legacy_files()
    
    # Paso 2: Migrar variables de entorno
    console.print(f"[{colors['info']}]🔑 Migrando configuración de APIs...[/]")
    env_vars = migrate_env_file()
    
    # Paso 3: Migrar historial
    console.print(f"[{colors['info']}]📚 Verificando historial...[/]")
    migrated_history_count = migrate_chat_history()
    
    # Paso 4: Crear configuración moderna
    console.print(f"[{colors['info']}]⚙️ Creando configuración moderna...[/]")
    modern_config = create_modern_config(env_vars)
    
    if not save_modern_config(modern_config):
        console.print(f"[{colors['error']}]❌ Error en la migración[/]")
        return
    
    # Paso 5: Actualizar scripts
    console.print(f"[{colors['info']}]🔧 Actualizando scripts...[/]")
    updated_scripts = update_scripts()
    
    # Mostrar resumen
    show_migration_summary(
        backed_up_files,
        migrated_history_count, 
        modern_config["configured_apis"],
        updated_scripts
    )
    
    console.print(f"\n[{colors['success']}]✅ ¡Migración completada exitosamente![/]")

if __name__ == "__main__":
    main()
