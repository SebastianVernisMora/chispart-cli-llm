#!/usr/bin/env python3
"""
🚀 Chispart Dev Agent v3.0 - Setup Wizard Interactivo
Configuración guiada paso a paso para nuevos usuarios
"""

import os
import sys
import json
import time
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.align import Align

console = Console()

class ChispartSetupWizard:
    def __init__(self):
        self.config_file = Path("config/chispart_config.json")
        self.env_file = Path(".env")
        self.is_termux = self.detect_termux()
        self.system_info = self.get_system_info()
        self.config = {}
        
    def detect_termux(self) -> bool:
        """Detecta si estamos ejecutando en Termux"""
        return os.environ.get('PREFIX', '').startswith('/data/data/com.termux')
    
    def get_system_info(self) -> Dict:
        """Obtiene información del sistema"""
        return {
            'platform': platform.system(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'is_termux': self.is_termux,
            'home_dir': str(Path.home()),
            'current_dir': str(Path.cwd())
        }
    
    def show_welcome(self):
        """Muestra pantalla de bienvenida"""
        welcome_text = """
🚀 ¡Bienvenido a Chispart Dev Agent v3.0!

Tu asistente de desarrollo con IA más poderoso
• 100+ Modelos de IA disponibles
• Gestión inteligente de equipos
• Ejecución segura de comandos
• Optimizado para móviles y desktop
        """
        
        panel = Panel(
            Align.center(welcome_text),
            title="🎉 Setup Wizard Interactivo",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
        
        # Mostrar información del sistema detectado
        system_table = Table(title="🔍 Sistema Detectado")
        system_table.add_column("Propiedad", style="cyan")
        system_table.add_column("Valor", style="green")
        
        system_table.add_row("Plataforma", self.system_info['platform'])
        system_table.add_row("Arquitectura", self.system_info['architecture'])
        system_table.add_row("Python", self.system_info['python_version'])
        system_table.add_row("Entorno", "Termux/Android" if self.is_termux else "Desktop/Servidor")
        
        console.print(system_table)
        console.print()
        
        if not Confirm.ask("¿Continuar con la configuración?", default=True):
            console.print("👋 ¡Hasta luego! Ejecuta este wizard cuando estés listo.")
            sys.exit(0)
    
    def check_dependencies(self) -> bool:
        """Verifica e instala dependencias necesarias"""
        console.print("\n🔍 [bold blue]Verificando dependencias...[/bold blue]")
        
        dependencies = [
            ("python3", "Python 3.8+"),
            ("pip", "Python Package Manager"),
            ("git", "Control de versiones")
        ]
        
        missing_deps = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for cmd, desc in dependencies:
                task = progress.add_task(f"Verificando {desc}...", total=None)
                
                try:
                    result = subprocess.run([cmd, "--version"], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        progress.update(task, description=f"✅ {desc} - OK")
                    else:
                        missing_deps.append((cmd, desc))
                        progress.update(task, description=f"❌ {desc} - No encontrado")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    missing_deps.append((cmd, desc))
                    progress.update(task, description=f"❌ {desc} - No encontrado")
                
                time.sleep(0.5)
        
        # Verificar git
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"{Colors.OKGREEN}✅ Git: {version}{Colors.ENDC}")
                dependencies['git'] = True
            else:
                print(f"{Colors.WARNING}⚠️ Git no encontrado (opcional){Colors.ENDC}")
        except Exception:
            print(f"{Colors.WARNING}⚠️ Git no disponible (opcional){Colors.ENDC}")
        
        # Verificar curl
        try:
            result = subprocess.run(['curl', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ curl: Disponible{Colors.ENDC}")
                dependencies['curl'] = True
            else:
                print(f"{Colors.WARNING}⚠️ curl no encontrado (opcional){Colors.ENDC}")
        except Exception:
            print(f"{Colors.WARNING}⚠️ curl no disponible (opcional){Colors.ENDC}")
        
        return dependencies
    
    def install_python_dependencies(self) -> bool:
        """Instala dependencias Python"""
        print(f"\n{Colors.HEADER}📦 PASO 2: Instalando Dependencias Python{Colors.ENDC}")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print(f"{Colors.FAIL}❌ Archivo requirements.txt no encontrado{Colors.ENDC}")
            return False
        
        try:
            print(f"{Colors.OKCYAN}📥 Instalando dependencias desde requirements.txt...{Colors.ENDC}")
            
            # Comando de instalación optimizado para Termux
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
            if self.is_termux:
                cmd.extend(['--no-cache-dir', '--disable-pip-version-check'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Dependencias instaladas correctamente{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.FAIL}❌ Error instalando dependencias:{Colors.ENDC}")
                print(f"{Colors.FAIL}{result.stderr}{Colors.ENDC}")
                return False
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error durante la instalación: {e}{Colors.ENDC}")
            return False
    
    def configure_apis(self) -> Dict[str, str]:
        """Configuración interactiva de APIs"""
        print(f"\n{Colors.HEADER}🔑 PASO 3: Configuración de APIs de IA{Colors.ENDC}")
        
        apis_info = {
            'chispart': {
                'name': 'Chispart AI',
                'description': '60+ modelos, General y Código',
                'url': 'https://chispart.ai/api',
                'required': True
            },
            'qwen': {
                'name': 'Qwen AI',
                'description': '13 modelos, Multilingüe y Razonamiento',
                'url': 'https://dashscope.aliyun.com',
                'required': False
            },
            'gemini': {
                'name': 'Google Gemini',
                'description': '8 modelos, Multimodal y Análisis',
                'url': 'https://makersuite.google.com/app/apikey',
                'required': False
            },
            'codestral': {
                'name': 'Mistral Codestral',
                'description': '5 modelos, Programación especializada',
                'url': 'https://console.mistral.ai',
                'required': False
            }
        }
        
        configured_apis = {}
        
        print(f"{Colors.OKCYAN}🎯 Necesitas configurar al menos una API para usar Chispart{Colors.ENDC}")
        print(f"{Colors.OKGREEN}💡 Recomendamos empezar con Chispart AI (gratuita para empezar){Colors.ENDC}")
        
        for api_key, api_info in apis_info.items():
            print(f"\n{Colors.BOLD}🔹 {api_info['name']}{Colors.ENDC}")
            print(f"   📝 {api_info['description']}")
            print(f"   🔗 Obtener API Key: {api_info['url']}")
            
            if api_info['required']:
                configure = True
