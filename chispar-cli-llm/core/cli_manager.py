"""
Gestor principal de la CLI de Chispart
Coordina todos los componentes y maneja el estado global
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from config import AVAILABLE_APIS, DEFAULT_API
from .command_handler import CommandHandler
from .validation import ConfigValidator, APIValidator
from .error_handler import ChispartErrorHandler, set_debug_mode
from ui.theme_manager import ThemeManager, get_theme
from ui.components import console, create_panel, create_table
from ui.interactive import SetupWizard, ThemeSelector

class ChispartCLIManager:
    """Gestor principal de la CLI de Chispart"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        set_debug_mode(debug_mode)
        
        # Inicializar componentes
        self.theme_manager = ThemeManager()
        self.colors = get_theme()  # Agregar acceso a colores del tema
        self.command_handler = CommandHandler(debug_mode)
        self.error_handler = ChispartErrorHandler(debug_mode)
        
        # Estado de la aplicación
        self.app_state = {
            "initialized": False,
            "current_api": DEFAULT_API,
            "current_theme": self.theme_manager.current_theme,
            "config_valid": False,
            "termux_environment": False
        }
        
        # Inicializar
        self._initialize()
    
    def _initialize(self) -> None:
        """Inicializa la CLI y verifica el entorno"""
        try:
            # Verificar entorno Termux
            termux_info = ConfigValidator.validate_termux_environment()
            self.app_state["termux_environment"] = termux_info["is_termux"]
            
            # Verificar configuración
            config_valid, configured_apis, missing_apis = ConfigValidator.validate_env_file()
            self.app_state["config_valid"] = config_valid
            self.app_state["configured_apis"] = configured_apis
            self.app_state["missing_apis"] = missing_apis
            
            # Mostrar recomendaciones de Termux si es necesario
            if termux_info["is_termux"] and termux_info["recommendations"]:
                self._show_termux_recommendations(termux_info["recommendations"])
            
            self.app_state["initialized"] = True
            
        except Exception as e:
            self.error_handler.handle_unexpected_error(e, {"component": "initialization"})
    
    def show_welcome(self) -> None:
        """Muestra mensaje de bienvenida"""
        colors = get_theme()
        
        # Banner principal
        from chispart_banner import get_chispart_isometric_filled
        banner = get_chispart_isometric_filled()
        console.print(banner)
        
        # Información de estado
        status_info = self._get_status_info()
        
        welcome_content = f"""
[{colors['primary']}]🚀 ¡Bienvenido a Chispart CLI![/]

[{colors['dim']}]Tu interfaz universal para múltiples APIs de IA[/]

{status_info}

[{colors['info']}]Comandos principales:[/]
[{colors['secondary']}]• chispart chat "mensaje" - Enviar mensaje[/]
[{colors['secondary']}]• chispart interactivo - Modo conversación[/]
[{colors['secondary']}]• chispart imagen archivo.jpg - Analizar imagen[/]
[{colors['secondary']}]• chispart pdf archivo.pdf - Analizar PDF[/]
[{colors['secondary']}]• chispart configure - Configurar APIs[/]
[{colors['secondary']}]• chispart --help - Ver ayuda completa[/]
"""
        
        console.print(create_panel(
            welcome_content,
            title="Chispart CLI",
            style="chispart.brand"
        ))
    
    def _get_status_info(self) -> str:
        """Obtiene información del estado actual"""
        colors = get_theme()
        
        if not self.app_state["config_valid"]:
            return f"[{colors['warning']}]⚠️ No hay APIs configuradas - Usa 'chispart configure' para empezar[/]"
        
        configured_count = len(self.app_state.get("configured_apis", []))
        total_apis = len(AVAILABLE_APIS)
        
        status_parts = [
            f"[{colors['success']}]✅ {configured_count}/{total_apis} APIs configuradas[/]",
            f"[{colors['info']}]🎨 Tema: {self.app_state['current_theme']}[/]"
        ]
        
        if self.app_state["termux_environment"]:
            status_parts.append(f"[{colors['accent']}]📱 Optimizado para Termux[/]")
        
        return "\n".join(status_parts)
    
    def show_status(self) -> None:
        """Muestra estado detallado del sistema"""
        colors = get_theme()
        
        # Tabla de APIs
        api_table = create_table(title="Estado de APIs")
        api_table.add_column("API", style="chispart.brand")
        api_table.add_column("Estado", style=self.colors["accent"])
        api_table.add_column("Modelos", style="chispart.dim")
        
        for api_key, api_info in AVAILABLE_APIS.items():
            # Verificar estado de la API
            valid, config, error = APIValidator.validate_api_key(api_key)
            
            if valid:
                status = f"[{colors['success']}]✅ Configurada[/]"
                from config import get_available_models
                models = get_available_models(api_key)
                model_count = f"{len(models)} modelos"
            else:
                status = f"[{colors['error']}]❌ No configurada[/]"
                model_count = "N/A"
            
            api_table.add_row(api_info["name"], status, model_count)
        
        console.print(api_table)
        
        # Estadísticas de uso
        stats = self.command_handler.get_stats()
        if stats["commands_executed"] > 0:
            stats_table = create_table(title="Estadísticas de Uso")
            stats_table.add_column("Métrica", style="chispart.brand")
            stats_table.add_column("Valor", style=self.colors["accent"])
            
            stats_table.add_row("Comandos ejecutados", str(stats["commands_executed"]))
            stats_table.add_row("Requests exitosos", str(stats["successful_requests"]))
            stats_table.add_row("Requests fallidos", str(stats["failed_requests"]))
            stats_table.add_row("Tokens totales usados", str(stats["total_tokens_used"]))
            
            success_rate = (stats["successful_requests"] / stats["commands_executed"]) * 100
            stats_table.add_row("Tasa de éxito", f"{success_rate:.1f}%")
            
            console.print(stats_table)
        
        # Información del entorno
        env_info = f"""
[{colors['primary']}]🔧 Información del Entorno[/]

[{colors['dim']}]Tema actual: {self.app_state['current_theme']}[/]
[{colors['dim']}]Modo debug: {'Activado' if self.debug_mode else 'Desactivado'}[/]
[{colors['dim']}]Entorno Termux: {'Sí' if self.app_state['termux_environment'] else 'No'}[/]
[{colors['dim']}]Directorio de trabajo: {os.getcwd()}[/]
"""
        
        console.print(create_panel(env_info, title="Entorno", style=self.colors["info"]))
    
    def run_setup_wizard(self) -> bool:
        """Ejecuta el asistente de configuración inicial"""
        try:
            wizard = SetupWizard(AVAILABLE_APIS, self.theme_manager)
            config_result = wizard.run()
            
            if config_result:
                # Guardar configuración de APIs
                if "api_keys" in config_result:
                    self._save_api_keys(config_result["api_keys"])
                
                # Actualizar estado
                self._initialize()
                
                return True
            
            return False
            
        except Exception as e:
            self.error_handler.handle_unexpected_error(e, {"component": "setup_wizard"})
            return False
    
    def configure_theme(self) -> bool:
        """Configura el tema interactivamente"""
        try:
            theme_selector = ThemeSelector(self.theme_manager)
            selected_theme = theme_selector.select_theme()
            
            if selected_theme:
                self.app_state["current_theme"] = selected_theme
                return True
            
            return False
            
        except Exception as e:
            self.error_handler.handle_unexpected_error(e, {"component": "theme_configuration"})
            return False
    
    def show_models(self, api_name: Optional[str] = None) -> None:
        """Muestra modelos disponibles"""
        if not api_name:
            api_name = self.app_state["current_api"]
        
        # Validar API
        valid, config, error = APIValidator.validate_api_key(api_name)
        if not valid:
            console.print(f"[red]❌ {error}[/red]")
            return
        
        from config import get_available_models, get_default_model
        available_models = get_available_models(api_name)
        default_model = get_default_model(api_name)
        
        # Tabla de modelos
        models_table = create_table(title=f"Modelos Disponibles - {config['name']}")
        models_table.add_column("Nombre", style="chispart.brand")
        models_table.add_column("ID del Modelo", style=self.colors["accent"])
        models_table.add_column("Estado", style="chispart.dim")
        
        # Descripciones de modelos
        model_descriptions = {
            "gpt-4": "Modelo GPT-4 estándar para texto",
            "gpt-4o": "GPT-4 Omni - Multimodal avanzado",
            "gpt-4-vision": "GPT-4 con capacidades de visión",
            "gpt-4-turbo": "GPT-4 Turbo - Más rápido y actualizado",
            "gpt-3.5-turbo": "Modelo más rápido y económico",
            "claude-3.5-sonnet": "Claude 3.5 Sonnet - El más avanzado",
            "claude-3-opus": "Claude 3 Opus - El más potente",
            "claude-3-sonnet": "Claude 3 Sonnet - Equilibrado",
            "claude-3-haiku": "Claude 3 Haiku - El más rápido",
            "llama-3.1-70b": "Llama 3.1 70B - Modelo grande",
            "llama-3.1-8b": "Llama 3.1 8B - Modelo rápido",
            "mixtral-8x7b": "Mixtral 8x7B - Mezcla de expertos",
            "gemini-2.5-flash": "Gemini 2.5 Flash - Última generación",
            "deepseek-r1": "DeepSeek R1 - Razonamiento avanzado"
        }
        
        for name, model_id in available_models.items():
            status = "🌟 Por defecto" if name == default_model else ""
            description = model_descriptions.get(name, f"Modelo de {config['name']}")
            
            models_table.add_row(name, model_id, status)
        
        console.print(models_table)
        console.print(f"\n[dim]Modelo por defecto: {default_model}[/dim]")
    
    def show_history(self, limit: int = 10) -> None:
        """Muestra historial de conversaciones"""
        from utils import load_conversation_history
        
        history = load_conversation_history()
        
        if not history:
            console.print("[yellow]No hay conversaciones en el historial[/yellow]")
            return
        
        # Mostrar las últimas conversaciones
        recent_conversations = history[-limit:]
        
        history_table = create_table(title="Historial de Conversaciones")
        history_table.add_column("Fecha", style=self.colors["accent"])
        history_table.add_column("Tipo", style="chispart.brand")
        history_table.add_column("API", style=self.colors["info"])
        history_table.add_column("Modelo", style=self.colors["secondary"])
        history_table.add_column("Contenido", style="chispart.dim")
        history_table.add_column("Tokens", style="chispart.warning")
        
        for conv in recent_conversations:
            timestamp = conv.get("timestamp", "N/A")
            if timestamp != "N/A":
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%m-%d %H:%M")
                except:
                    timestamp = "N/A"
            
            conv_type = conv.get("type", "N/A")
            api = conv.get("api", "N/A")
            model = conv.get("model", "N/A")
            
            # Obtener contenido
            if conv_type == "chat":
                content = conv.get("message", "N/A")
            elif conv_type in ["image", "pdf"]:
                file_name = os.path.basename(conv.get("file", "N/A"))
                content = f"{file_name}"
            else:
                content = conv.get("message", "N/A")
            
            # Truncar contenido si es muy largo
            if len(content) > 40:
                content = content[:37] + "..."
            
            tokens = str(conv.get("usage", {}).get("total_tokens", "N/A")) if conv.get("usage") else "N/A"
            
            history_table.add_row(timestamp, conv_type, api, model, content, tokens)
        
        console.print(history_table)
        
        if len(history) > limit:
            console.print(f"\n[dim]Mostrando las últimas {limit} de {len(history)} conversaciones[/dim]")
    
    def _save_api_keys(self, api_keys: Dict[str, str]) -> None:
        """Guarda claves API en archivo .env"""
        env_file = ".env"
        env_vars = {}
        
        # Leer archivo existente si existe
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"')
            except Exception as e:
                console.print(f"[yellow]Advertencia: Error leyendo .env existente: {e}[/yellow]")
        
        # Actualizar con nuevas claves
        env_vars.update(api_keys)
        
        # Escribir archivo
        try:
            with open(env_file, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f'{key}="{value}"\n')
            
            colors = get_theme()
            console.print(f"[{colors['success']}]✅ Claves API guardadas en {env_file}[/]")
            
        except Exception as e:
            self.error_handler.handle_file_error(e, env_file, "escribir")
    
    def _show_termux_recommendations(self, recommendations: List[str]) -> None:
        """Muestra recomendaciones para Termux"""
        if not recommendations:
            return
        
        colors = get_theme()
        
        rec_content = f"[{colors['warning']}]📱 Recomendaciones para Termux:[/]\n\n"
        for rec in recommendations:
            rec_content += f"[{colors['info']}]• {rec}[/]\n"
        
        console.print(create_panel(
            rec_content,
            title="Optimización Termux",
            style="chispart.warning"
        ))
    
    def set_current_api(self, api_name: str) -> bool:
        """Establece la API actual"""
        if api_name not in AVAILABLE_APIS:
            console.print(f"[red]❌ API '{api_name}' no soportada[/red]")
            return False
        
        # Validar que esté configurada
        valid, config, error = APIValidator.validate_api_key(api_name)
        if not valid:
            console.print(f"[red]❌ {error}[/red]")
            return False
        
        self.app_state["current_api"] = api_name
        colors = get_theme()
        console.print(f"[{colors['success']}]✅ API actual cambiada a {config['name']}[/]")
        return True
    
    def get_current_api(self) -> str:
        """Obtiene la API actual"""
        return self.app_state["current_api"]
    
    def is_ready(self) -> bool:
        """Verifica si la CLI está lista para usar"""
        return self.app_state["initialized"] and self.app_state["config_valid"]
    
    def get_app_state(self) -> Dict[str, Any]:
        """Obtiene el estado completo de la aplicación"""
        return self.app_state.copy()
    
    def cleanup(self) -> None:
        """Limpia recursos al cerrar la aplicación"""
        # Guardar configuración si es necesario
        # Cerrar conexiones, etc.
        pass
