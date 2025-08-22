"""
Cliente para interactuar con múltiples APIs de LLM
"""
import requests
import json
from typing import List, Dict, Any, Optional
from config import REQUEST_TIMEOUT


class APIError(Exception):
    """Excepción personalizada para errores de la API"""
    def __init__(self, message: str, status_code: Optional[int] = None, api_name: str = "Unknown"):
        self.message = message
        self.status_code = status_code
        self.api_name = api_name
        super().__init__(self.message)


class UniversalAPIClient:
    """Cliente universal para múltiples APIs de LLM"""
    
    def __init__(self, api_key: str, base_url: str, api_name: str = "Unknown"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.api_name = api_name
        self.session = requests.Session()
        
        # Configurar headers según la API
        if api_name.lower() == "anthropic":
            self.session.headers.update({
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            })
        else:
            # Para OpenAI, BlackboxAI, Groq, Together, etc.
            self.session.headers.update({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            })
    
    def chat_completions(self, messages: List[Dict[str, Any]], model: str) -> Dict[str, Any]:
        """
        Envía una solicitud de chat completion a la API
        
        Args:
            messages: Lista de mensajes en formato OpenAI
            model: Modelo a utilizar
            
        Returns:
            Respuesta de la API
            
        Raises:
            APIError: Si hay un error en la API
        """
        # Determinar endpoint según la API
        if self.api_name.lower() == "anthropic":
            url = f"{self.base_url}/v1/messages"
            payload = self._format_anthropic_payload(messages, model)
        else:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": model,
                "messages": messages
            }
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                api_response = response.json()
                # Normalizar respuesta de Anthropic al formato OpenAI
                if self.api_name.lower() == "anthropic":
                    return self._normalize_anthropic_response(api_response)
                return api_response
            else:
                error_msg = f"Error de API {self.api_name}: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        if isinstance(error_data["error"], dict):
                            error_msg = error_data["error"].get("message", error_msg)
                        else:
                            error_msg = str(error_data["error"])
                    elif "message" in error_data:
                        error_msg = error_data["message"]
                except:
                    error_msg = f"Error de API {self.api_name}: {response.status_code} - {response.text}"
                
                raise APIError(error_msg, response.status_code, self.api_name)
                
        except requests.exceptions.Timeout:
            raise APIError(f"Timeout: La solicitud a {self.api_name} tardó demasiado tiempo", api_name=self.api_name)
        except requests.exceptions.ConnectionError:
            raise APIError(f"Error de conexión: No se pudo conectar a {self.api_name}", api_name=self.api_name)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Error de solicitud a {self.api_name}: {str(e)}", api_name=self.api_name)
    
    def _format_anthropic_payload(self, messages: List[Dict[str, Any]], model: str) -> Dict[str, Any]:
        """Formatea el payload para la API de Anthropic"""
        # Separar system message si existe
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        payload = {
            "model": model,
            "max_tokens": 4000,
            "messages": user_messages
        }
        
        if system_message:
            payload["system"] = system_message
            
        return payload
    
    def _normalize_anthropic_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza la respuesta de Anthropic al formato OpenAI"""
        content = ""
        if "content" in response and response["content"]:
            if isinstance(response["content"], list):
                content = response["content"][0].get("text", "")
            else:
                content = response["content"]
        
        return {
            "id": response.get("id", ""),
            "object": "chat.completion",
            "created": 0,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": response.get("stop_reason", "stop")
            }],
            "usage": response.get("usage", {})
        }
    
    def extract_response_content(self, api_response: Dict[str, Any]) -> str:
        """
        Extrae el contenido de la respuesta de la API
        
        Args:
            api_response: Respuesta completa de la API
            
        Returns:
            Contenido del mensaje de respuesta
        """
        try:
            return api_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "Error: No se pudo extraer la respuesta"
    
    def get_usage_info(self, api_response: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """
        Extrae información de uso de tokens de la respuesta
        
        Args:
            api_response: Respuesta completa de la API
            
        Returns:
            Información de uso de tokens o None si no está disponible
        """
        return api_response.get("usage")


# Mantener compatibilidad con el nombre anterior
BlackboxAPIClient = UniversalAPIClient
BlackboxAPIError = APIError
