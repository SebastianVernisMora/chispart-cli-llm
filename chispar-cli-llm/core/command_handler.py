"""
Manejador de comandos centralizado para Chispart CLI
"""

import os
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from api_client import UniversalAPIClient, APIError
from utils import (
    create_image_data_url, extract_text_from_pdf, 
    save_conversation_history, load_conversation_history
)
from .validation import validate_complete_request, InputValidator
from .error_handler import ChispartErrorHandler, handle_errors
from ui.components import console, create_panel, create_progress_bar
from ui.theme_manager import get_theme

class CommandHandler:
    """Manejador centralizado para todos los comandos de Chispart"""
    
    def __init__(self, debug_mode: bool = False):
        self.error_handler = ChispartErrorHandler(debug_mode)
        self.colors = get_theme()
        self.stats = {
            "commands_executed": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0
        }
    
    @handle_errors(ChispartErrorHandler(), exit_on_error=False)
    def handle_chat(self, api_name: str, message: str, model: Optional[str] = None, 
                   save_history: bool = True, stream: bool = False) -> Dict[str, Any]:
        """
        Maneja comandos de chat
        
        Returns:
            Dict con resultado de la operación
        """
        self.stats["commands_executed"] += 1
        
        # Validación completa
        valid, validation_data, error = validate_complete_request(
            api_name=api_name,
            model=model,
            message=message
        )
        
        if not valid:
            self.stats["failed_requests"] += 1
            raise ValueError(error)
        
        config = validation_data["config"]
        validated_model = validation_data["model"]
        
        # Mostrar información de la request
        self._show_request_info("Chat", config["name"], validated_model, message)
        
        # Crear cliente y enviar request
        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        
        try:
            with console.status(f"[{self.colors['primary']}]Enviando mensaje a {config['name']}..."):
                messages = [{"role": "user", "content": message}]
                
                # Obtener nombre real del modelo
                from config import get_available_models
                available_models = get_available_models(api_name)
                model_name = available_models[validated_model]
                
                start_time = time.time()
                response = client.chat_completions(messages, model_name, stream=stream)
                execution_time = time.time() - start_time
            
            # Extraer contenido y mostrar respuesta
            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)
            
            self._show_response(content, config["name"], execution_time, usage)
            
            # Guardar en historial
            if save_history:
                conversation = {
                    "type": "chat",
                    "api": api_name,
                    "model": validated_model,
                    "message": message,
                    "response": content,
                    "usage": usage,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time
                }
                save_conversation_history(conversation)
            
            # Actualizar estadísticas
            self.stats["successful_requests"] += 1
            if usage and "total_tokens" in usage:
                self.stats["total_tokens_used"] += usage["total_tokens"]
            
            return {
                "success": True,
                "response": content,
                "usage": usage,
                "execution_time": execution_time,
                "model_used": validated_model,
                "api_used": config["name"]
            }
            
        except APIError as e:
            self.stats["failed_requests"] += 1
            self.error_handler.handle_api_error(e, {
                "api_name": api_name,
                "model": validated_model,
                "message_length": len(message)
            })
            raise
    
    @handle_errors(ChispartErrorHandler(), exit_on_error=False)
    def handle_image_analysis(self, api_name: str, file_path: str, prompt: str = "¿Qué hay en esta imagen?",
                            model: Optional[str] = None, save_history: bool = True) -> Dict[str, Any]:
        """Maneja análisis de imágenes"""
        self.stats["commands_executed"] += 1
        
        # Validación completa
        valid, validation_data, error = validate_complete_request(
            api_name=api_name,
            model=model,
            message=prompt,
            file_path=file_path,
            file_type="image"
        )
        
        if not valid:
            self.stats["failed_requests"] += 1
            raise ValueError(error)
        
        config = validation_data["config"]
        validated_model = validation_data["model"]
        file_info = validation_data["file_info"]
        
        # Optimizar prompt para imágenes
        _, optimized_prompt, _ = InputValidator.validate_prompt(prompt, "image")
        
        # Mostrar información de la request
        self._show_request_info("Análisis de Imagen", config["name"], validated_model, 
                              f"{file_info['name']} ({file_info['size_formatted']})")
        
        # Crear cliente y procesar imagen
        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        
        try:
            with console.status(f"[{self.colors['primary']}]Analizando imagen con {config['name']}..."):
                # Crear mensaje con imagen
                image_url = create_image_data_url(file_path)
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": optimized_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }]
                
                # Obtener nombre real del modelo
                from config import get_available_models
                available_models = get_available_models(api_name)
                model_name = available_models[validated_model]
                
                start_time = time.time()
                response = client.chat_completions(messages, model_name)
                execution_time = time.time() - start_time
            
            # Extraer contenido y mostrar respuesta
            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)
            
            self._show_response(content, config["name"], execution_time, usage, 
                              f"Análisis de {file_info['name']}")
            
            # Guardar en historial
            if save_history:
                conversation = {
                    "type": "image",
                    "api": api_name,
                    "model": validated_model,
                    "file": file_path,
                    "prompt": optimized_prompt,
                    "response": content,
                    "usage": usage,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time,
                    "file_info": file_info
                }
                save_conversation_history(conversation)
            
            # Actualizar estadísticas
            self.stats["successful_requests"] += 1
            if usage and "total_tokens" in usage:
                self.stats["total_tokens_used"] += usage["total_tokens"]
            
            return {
                "success": True,
                "response": content,
                "usage": usage,
                "execution_time": execution_time,
                "model_used": validated_model,
                "api_used": config["name"],
                "file_analyzed": file_info['name']
            }
            
        except APIError as e:
            self.stats["failed_requests"] += 1
            self.error_handler.handle_api_error(e, {
                "api_name": api_name,
                "model": validated_model,
                "file_path": file_path,
                "file_size": file_info.get('size', 0)
            })
            raise
    
    @handle_errors(ChispartErrorHandler(), exit_on_error=False)
    def handle_pdf_analysis(self, api_name: str, file_path: str, prompt: str = "Resume el contenido de este documento",
                          model: Optional[str] = None, save_history: bool = True) -> Dict[str, Any]:
        """Maneja análisis de PDFs"""
        self.stats["commands_executed"] += 1
        
        # Validación completa
        valid, validation_data, error = validate_complete_request(
            api_name=api_name,
            model=model,
            message=prompt,
            file_path=file_path,
            file_type="pdf"
        )
        
        if not valid:
            self.stats["failed_requests"] += 1
            raise ValueError(error)
        
        config = validation_data["config"]
        validated_model = validation_data["model"]
        file_info = validation_data["file_info"]
        
        # Optimizar prompt para PDFs
        _, optimized_prompt, _ = InputValidator.validate_prompt(prompt, "pdf")
        
        # Mostrar información de la request
        self._show_request_info("Análisis de PDF", config["name"], validated_model,
                              f"{file_info['name']} ({file_info['size_formatted']})")
        
        # Crear cliente y procesar PDF
        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        
        try:
            with console.status(f"[{self.colors['primary']}]Extrayendo texto del PDF..."):
                # Extraer texto del PDF
                pdf_text = extract_text_from_pdf(file_path)
                
                # Limitar texto si es muy largo
                max_chars = 100000
                if len(pdf_text) > max_chars:
                    pdf_text = pdf_text[:max_chars] + "\n\n[... CONTENIDO TRUNCADO ...]"
                
                # Crear prompt completo
                full_prompt = f"""Se ha extraído el siguiente texto de un documento PDF ('{file_info['name']}'):

---
{pdf_text}
---

Por favor, responde a la siguiente pregunta basada en el texto del documento:

{optimized_prompt}"""
            
            with console.status(f"[{self.colors['primary']}]Analizando PDF con {config['name']}..."):
                messages = [{"role": "user", "content": full_prompt}]
                
                # Obtener nombre real del modelo
                from config import get_available_models
                available_models = get_available_models(api_name)
                model_name = available_models[validated_model]
                
                start_time = time.time()
                response = client.chat_completions(messages, model_name)
                execution_time = time.time() - start_time
            
            # Extraer contenido y mostrar respuesta
            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)
            
            self._show_response(content, config["name"], execution_time, usage,
                              f"Análisis de {file_info['name']}")
            
            # Guardar en historial
            if save_history:
                conversation = {
                    "type": "pdf",
                    "api": api_name,
                    "model": validated_model,
                    "file": file_path,
                    "prompt": optimized_prompt,
                    "response": content,
                    "usage": usage,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time,
                    "file_info": file_info,
                    "text_length": len(pdf_text)
                }
                save_conversation_history(conversation)
            
            # Actualizar estadísticas
            self.stats["successful_requests"] += 1
            if usage and "total_tokens" in usage:
                self.stats["total_tokens_used"] += usage["total_tokens"]
            
            return {
                "success": True,
                "response": content,
                "usage": usage,
                "execution_time": execution_time,
                "model_used": validated_model,
                "api_used": config["name"],
                "file_analyzed": file_info['name'],
                "text_extracted_length": len(pdf_text)
            }
            
        except APIError as e:
            self.stats["failed_requests"] += 1
            self.error_handler.handle_api_error(e, {
                "api_name": api_name,
                "model": validated_model,
                "file_path": file_path,
                "file_size": file_info.get('size', 0)
            })
            raise
    
    def handle_interactive_session(self, api_name: str, model: Optional[str] = None) -> None:
        """Maneja sesiones interactivas"""
        # Validación inicial
        valid, validation_data, error = validate_complete_request(
            api_name=api_name,
            model=model,
            message="test"  # Mensaje dummy para validación
        )
        
        if not valid:
            raise ValueError(error)
        
        config = validation_data["config"]
        validated_model = validation_data["model"]
        
        # Crear cliente
        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        messages = []
        
        # Mostrar información de la sesión
        session_info = f"""
[{self.colors['primary']}]🤖 Sesión interactiva con {config['name']}[/]

[{self.colors['dim']}]Modelo: {validated_model}[/]
[{self.colors['dim']}]Comandos especiales:[/]
[{self.colors['info']}]• 'salir', 'exit', 'quit' - Terminar sesión[/]
[{self.colors['info']}]• 'limpiar', 'clear' - Limpiar historial de sesión[/]
[{self.colors['info']}]• 'stats' - Ver estadísticas de la sesión[/]
"""
        
        console.print(create_panel(
            session_info,
            title="Modo Interactivo",
            style="chispart.brand"
        ))
        
        session_stats = {"messages_sent": 0, "total_tokens": 0}
        
        while True:
            try:
                # Obtener input del usuario
                from ui.interactive import InteractivePrompt
                user_input = InteractivePrompt.ask(f"[{self.colors['accent']}]Tú")
                
                # Comandos especiales
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    console.print(f"[{self.colors['success']}]¡Hasta luego! Mensajes enviados: {session_stats['messages_sent']}[/]")
                    break
                elif user_input.lower() in ['limpiar', 'clear']:
                    messages = []
                    console.print(f"[{self.colors['warning']}]Historial de sesión limpiado[/]")
                    continue
                elif user_input.lower() == 'stats':
                    self._show_session_stats(session_stats)
                    continue
                elif not user_input.strip():
                    continue
                
                # Validar mensaje
                valid_msg, msg_error = InputValidator.validate_message(user_input)
                if not valid_msg:
                    console.print(f"[{self.colors['error']}]❌ {msg_error}[/]")
                    continue
                
                # Agregar mensaje del usuario
                messages.append({"role": "user", "content": user_input})
                session_stats["messages_sent"] += 1
                
                # Enviar a la API
                try:
                    with console.status(f"[{self.colors['primary']}]Pensando con {config['name']}..."):
                        from config import get_available_models
                        available_models = get_available_models(api_name)
                        model_name = available_models[validated_model]
                        
                        response = client.chat_completions(messages, model_name)
                    
                    # Obtener y mostrar respuesta
                    content = client.extract_response_content(response)
                    usage = client.get_usage_info(response)
                    
                    console.print(f"[{self.colors['primary']}]{config['name']}:[/] {content}\n")
                    
                    # Agregar respuesta al historial de la sesión
                    messages.append({"role": "assistant", "content": content})
                    
                    # Actualizar estadísticas de sesión
                    if usage and "total_tokens" in usage:
                        session_stats["total_tokens"] += usage["total_tokens"]
                    
                    # Guardar conversación
                    conversation = {
                        "type": "interactive",
                        "api": api_name,
                        "model": validated_model,
                        "message": user_input,
                        "response": content,
                        "usage": usage,
                        "timestamp": datetime.now().isoformat()
                    }
                    save_conversation_history(conversation)
                    
                except APIError as e:
                    self.error_handler.handle_api_error(e, {
                        "api_name": api_name,
                        "model": validated_model,
                        "session_messages": len(messages)
                    })
                    # No terminar la sesión por un error, permitir continuar
                    
            except KeyboardInterrupt:
                console.print(f"\n[{self.colors['warning']}]Sesión interrumpida. ¡Hasta luego![/]")
                break
            except Exception as e:
                self.error_handler.handle_unexpected_error(e, {
                    "api_name": api_name,
                    "model": validated_model,
                    "session_messages": len(messages)
                })
                # Continuar la sesión
    
    def _show_request_info(self, request_type: str, api_name: str, model: str, content_info: str) -> None:
        """Muestra información de la request"""
        info = f"""
[{self.colors['primary']}]📤 {request_type}[/]
[{self.colors['dim']}]API: {api_name}[/]
[{self.colors['dim']}]Modelo: {model}[/]
[{self.colors['dim']}]Contenido: {content_info}[/]
"""
        console.print(info)
    
    def _show_response(self, content: str, api_name: str, execution_time: float, 
                      usage: Optional[Dict[str, Any]] = None, title: str = "Respuesta") -> None:
        """Muestra la respuesta de la API"""
        from rich.markdown import Markdown
        
        # Mostrar respuesta principal
        console.print(create_panel(
            Markdown(content),
            title=f"[{self.colors['primary']}]{title} - {api_name}[/]",
            style="chispart.brand"
        ))
        
        # Mostrar información adicional
        info_parts = [f"⏱️ {execution_time:.2f}s"]
        
        if usage:
            if "total_tokens" in usage:
                info_parts.append(f"🔢 {usage['total_tokens']} tokens")
            if "prompt_tokens" in usage and "completion_tokens" in usage:
                info_parts.append(f"({usage['prompt_tokens']}+{usage['completion_tokens']})")
        
        console.print(f"[{self.colors['dim']}]{' | '.join(info_parts)}[/]\n")
    
    def _show_session_stats(self, session_stats: Dict[str, Any]) -> None:
        """Muestra estadísticas de la sesión"""
        from ui.components import create_table
        
        table = create_table(title="Estadísticas de Sesión")
        table.add_column("Métrica", style="chispart.brand")
        table.add_column("Valor", style=self.colors["accent"])
        
        table.add_row("Mensajes enviados", str(session_stats["messages_sent"]))
        table.add_row("Tokens totales", str(session_stats["total_tokens"]))
        
        console.print(table)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del manejador"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Resetea las estadísticas"""
        self.stats = {
            "commands_executed": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0
        }
