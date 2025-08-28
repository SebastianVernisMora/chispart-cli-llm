"""
Comandos utilitarios y de información
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn

from ui.components import console, create_panel, create_table
from ui.theme_manager import get_theme
from core.error_handler import ChispartErrorHandler
from utils import load_conversation_history, format_file_size
from config_extended import get_available_models, get_default_model, AVAILABLE_APIS


class UtilityCommands:
    """Maneja comandos utilitarios del sistema"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.colors = get_theme()
    
    def handle_show_models(self, api_name: str) -> Dict[str, Any]:
        """
        Muestra los modelos disponibles para una API
        
        Args:
            api_name: Nombre de la API
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            if api_name not in AVAILABLE_APIS:
                error_msg = f"API '{api_name}' no reconocida"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
            
            available_models = get_available_models(api_name)
            default_model = get_default_model(api_name)
            api_info = AVAILABLE_APIS[api_name]
            
            self._display_models_table(api_name, api_info['name'], available_models, default_model)
            
            return {
                "success": True,
                "api": api_name,
                "models": available_models,
                "default_model": default_model
            }
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "show_models")
    
    def handle_show_history(self, limit: int = 10, filter_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Muestra el historial de conversaciones
        
        Args:
            limit: Número máximo de conversaciones a mostrar
            filter_type: Filtrar por tipo de conversación (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            history = load_conversation_history()
            
            if not history:
                console.print(f"[{self.colors['warning']}]📝 No hay conversaciones en el historial[/]")
                return {"success": True, "history": [], "total": 0}
            
            # Filtrar por tipo si se especifica
            if filter_type:
                history = [conv for conv in history if conv.get("type") == filter_type]
            
            # Limitar resultados
            recent_conversations = history[-limit:] if limit > 0 else history
            
            self._display_history_table(recent_conversations, len(history))
            
            return {
                "success": True,
                "history": recent_conversations,
                "total": len(history),
                "filtered": len(recent_conversations)
            }
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "show_history")
    
    def handle_system_info(self) -> Dict[str, Any]:
        """Muestra información del sistema"""
        try:
            system_info = self._gather_system_info()
            self._display_system_info(system_info)
            return {"success": True, "system_info": system_info}
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "system_info")
    
    def handle_clear_history(self, confirm: bool = False, 
                           older_than_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Limpia el historial de conversaciones
        
        Args:
            confirm: Si ya se confirmó la acción
            older_than_days: Solo eliminar conversaciones más antiguas que X días
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            from rich.prompt import Confirm
            
            # Cargar historial actual
            history = load_conversation_history()
            if not history:
                console.print(f"[{self.colors['info']}]📝 El historial ya está vacío[/]")
                return {"success": True, "cleared": 0}
            
            # Determinar qué conversaciones eliminar
            if older_than_days:
                cutoff_date = datetime.now() - timedelta(days=older_than_days)
                conversations_to_keep = []
                conversations_to_remove = []
                
                for conv in history:
                    try:
                        conv_date = datetime.fromisoformat(conv.get("timestamp", ""))
                        if conv_date > cutoff_date:
                            conversations_to_keep.append(conv)
                        else:
                            conversations_to_remove.append(conv)
                    except:
                        # Si no se puede parsear la fecha, mantener la conversación
                        conversations_to_keep.append(conv)
                
                total_to_remove = len(conversations_to_remove)
                action_desc = f"conversaciones anteriores a {older_than_days} días"
            else:
                conversations_to_keep = []
                total_to_remove = len(history)
                action_desc = "todo el historial"
            
            if total_to_remove == 0:
                console.print(f"[{self.colors['info']}]📝 No hay conversaciones que eliminar[/]")
                return {"success": True, "cleared": 0}
            
            # Pedir confirmación si no se proporcionó
            if not confirm:
                confirm = Confirm.ask(
                    f"[{self.colors['warning']}]⚠️ ¿Estás seguro de eliminar {action_desc} ({total_to_remove} conversaciones)?[/]",
                    default=False
                )
            
            if not confirm:
                console.print(f"[{self.colors['info']}]Operación cancelada[/]")
                return {"success": False, "error": "Operación cancelada"}
            
            # Guardar historial filtrado
            from utils import save_conversation_history
            
            # Si hay conversaciones que mantener, guardarlas
            if conversations_to_keep:
                # Reescribir el archivo con solo las conversaciones a mantener
                history_file = "chat_history.json"
                import json
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(conversations_to_keep, f, ensure_ascii=False, indent=2)
            else:
                # Eliminar el archivo completamente
                history_file = "chat_history.json"
                if os.path.exists(history_file):
                    os.remove(history_file)
            
            console.print(f"[{self.colors['success']}]✅ {total_to_remove} conversaciones eliminadas del historial[/]")
            return {"success": True, "cleared": total_to_remove}
            
        except Exception as e:
            return self.error_handler.handle_command_error(e, "clear_history")
    
    def handle_export_history(self, output_file: Optional[str] = None, 
                            format_type: str = "json") -> Dict[str, Any]:
        """
        Exporta el historial a un archivo
        
        Args:
            output_file: Archivo de salida (opcional)
            format_type: Formato de exportación (json, txt, csv)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            history = load_conversation_history()
            if not history:
                console.print(f"[{self.colors['warning']}]📝 No hay historial para exportar[/]")
                return {"success": False, "error": "Historial vacío"}
            
            # Generar nombre de archivo si no se proporciona
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"chispart_history_{timestamp}.{format_type}"
            
            # Exportar según el formato
            if format_type.lower() == "json":
                success = self._export_json(history, output_file)
            elif format_type.lower() == "txt":
                success = self._export_txt(history, output_file)
            elif format_type.lower() == "csv":
                success = self._export_csv(history, output_file)
            else:
                error_msg = f"Formato '{format_type}' no soportado. Use: json, txt, csv"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
            
            if success:
                file_size = format_file_size(os.path.getsize(output_file))
                console.print(f"[{self.colors['success']}]✅ Historial exportado a '{output_file}' ({file_size})[/]")
                return {"success": True, "file": output_file, "conversations": len(history)}
            else:
                error_msg = "Error durante la exportación"
                console.print(f"[{self.colors['error']}]{error_msg}[/]")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return self.error_handler.handle_command_error(e, "export_history")
    
    def _display_models_table(self, api_key: str, api_name: str, 
                            models: Dict[str, str], default_model: str):
        """Muestra tabla de modelos disponibles"""
        table = create_table(f"Modelos Disponibles - {api_name}")
        table.add_column("Nombre", style=self.colors['primary'])
        table.add_column("ID del Modelo", style=self.colors['info'])
        table.add_column("Estado", style=self.colors['success'])
        
        # Descripciones de modelos comunes
        model_descriptions = {
            "gpt-4": "Modelo GPT-4 estándar para texto",
            "gpt-4o": "GPT-4 Omni - Multimodal avanzado",
            "gpt-4-turbo": "GPT-4 Turbo - Más rápido y actualizado",
            "gpt-3.5-turbo": "Modelo más rápido y económico",
            "claude-3.5-sonnet": "Claude 3.5 Sonnet - Más avanzado",
            "claude-3-opus": "Claude 3 Opus - El más potente",
            "claude-3-sonnet": "Claude 3 Sonnet - Equilibrado",
            "claude-3-haiku": "Claude 3 Haiku - El más rápido",
            "llama-3.1-70b": "Llama 3.1 70B - Modelo grande",
            "llama-3.1-8b": "Llama 3.1 8B - Modelo rápido",
            "mixtral-8x7b": "Mixtral 8x7B - Mezcla de expertos",
            "gemini-2.5-flash": "Gemini 2.5 Flash - Última versión",
            "deepseek-r1": "DeepSeek R1 - Razonamiento avanzado"
        }
        
        for name, model_id in models.items():
            status = "⭐ Por defecto" if name == default_model else ""
            table.add_row(name, model_id, status)
        
        console.print(table)
        
        # Mostrar información adicional
        info_text = f"""
[{self.colors['info']}]💡 Información:[/]
[{self.colors['dim']}]• Total de modelos: {len(models)}[/]
[{self.colors['dim']}]• Modelo por defecto: {default_model}[/]
[{self.colors['dim']}]• API: {api_name}[/]
"""
        
        console.print(create_panel(
            info_text.strip(),
            title="Información de Modelos",
            style=colors["info"]
        ))
    
    def _display_history_table(self, conversations: List[Dict[str, Any]], total_count: int):
        """Muestra tabla del historial de conversaciones"""
        table = create_table("Historial de Conversaciones")
        table.add_column("Fecha", style=self.colors['dim'])
        table.add_column("Tipo", style=self.colors['primary'])
        table.add_column("API", style=self.colors['info'])
        table.add_column("Modelo", style=self.colors['success'])
        table.add_column("Contenido", style=self.colors['dim'])
        table.add_column("Tokens", style=self.colors['warning'])
        
        for conv in conversations:
            # Formatear fecha
            timestamp = conv.get("timestamp", "N/A")
            if timestamp != "N/A":
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_date = dt.strftime("%m/%d %H:%M")
                except:
                    formatted_date = "N/A"
            else:
                formatted_date = "N/A"
            
            # Obtener información básica
            conv_type = conv.get("type", "N/A")
            api_name = conv.get("api", "N/A")
            model = conv.get("model", "N/A")
            
            # Obtener contenido (truncado)
            if conv_type == "chat":
                content = conv.get("message", "N/A")
            elif conv_type in ["image", "pdf"]:
                content = conv.get("file", "N/A")
            else:
                content = conv.get("message", conv.get("file", "N/A"))
            
            # Truncar contenido si es muy largo
            if len(content) > 40:
                content = content[:37] + "..."
            
            # Obtener tokens
            usage = conv.get("usage", {})
            tokens = str(usage.get("total_tokens", "N/A")) if usage else "N/A"
            
            table.add_row(formatted_date, conv_type, api_name, model, content, tokens)
        
        console.print(table)
        
        # Mostrar resumen
        if len(conversations) < total_count:
            console.print(f"[{self.colors['dim']}]Mostrando {len(conversations)} de {total_count} conversaciones totales[/]")
    
    def _display_system_info(self, system_info: Dict[str, Any]):
        """Muestra información del sistema"""
        info_text = f"""
[{self.colors['primary']}]🖥️ Información del Sistema[/]

[{self.colors['info']}]Sistema Operativo:[/] {system_info['os']}
[{self.colors['info']}]Versión de Python:[/] {system_info['python_version']}
[{self.colors['info']}]Directorio actual:[/] {system_info['current_dir']}
[{self.colors['info']}]Directorio home:[/] {system_info['home_dir']}

[{self.colors['primary']}]📦 Chispart CLI[/]
[{self.colors['info']}]Versión:[/] {system_info['chispart_version']}
[{self.colors['info']}]Directorio de instalación:[/] {system_info['install_dir']}
[{self.colors['info']}]Archivo de configuración:[/] {system_info['config_file']}
[{self.colors['info']}]Archivo de historial:[/] {system_info['history_file']}

[{self.colors['primary']}]🔧 Dependencias[/]
"""
        
        # Añadir estado de dependencias
        for dep, status in system_info['dependencies'].items():
            status_icon = "✅" if status else "❌"
            info_text += f"[{self.colors['dim']}]  {status_icon} {dep}[/]\n"
        
        console.print(create_panel(
            info_text.strip(),
            title="Información del Sistema",
            style="chispart.brand"
        ))
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Recopila información del sistema"""
        import platform
        
        # Verificar dependencias
        dependencies = {}
        required_modules = ['click', 'rich', 'requests', 'flask', 'PIL', 'dotenv']
        
        for module in required_modules:
            try:
                __import__(module)
                dependencies[module] = True
            except ImportError:
                dependencies[module] = False
        
        # Verificar dependencias opcionales
        optional_modules = ['fitz', 'pypdf']
        for module in optional_modules:
            try:
                __import__(module)
                dependencies[f"{module} (opcional)"] = True
            except ImportError:
                dependencies[f"{module} (opcional)"] = False
        
        return {
            'os': f"{platform.system()} {platform.release()}",
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'current_dir': str(Path.cwd()),
            'home_dir': str(Path.home()),
            'chispart_version': "2.0.0-modern",
            'install_dir': str(Path(__file__).parent.parent),
            'config_file': str(Path.cwd() / ".env"),
            'history_file': str(Path.cwd() / "chat_history.json"),
            'dependencies': dependencies
        }
    
    def _export_json(self, history: List[Dict[str, Any]], output_file: str) -> bool:
        """Exporta historial en formato JSON"""
        try:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
