"""
Cliente para interactuar con múltiples APIs de LLM
"""
import requests
import json
import time
from typing import List, Dict, Any, Optional
from config_extended import REQUEST_TIMEOUT, CONNECT_TIMEOUT, READ_TIMEOUT, MOBILE_NETWORK_CONFIG

# Importar utilidades de Termux si están disponibles
try:
    from termux_utils import is_termux
except ImportError:
    def is_termux():
        return False


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
    
    def chat_completions(self, messages: List[Dict[str, Any]], model: str, stream: bool = False):
        """
        Envía una solicitud de chat completion a la API.
        
        Args:
            messages: Lista de mensajes en formato OpenAI.
            model: Modelo a utilizar.
            stream: Si es True, devuelve un generador de chunks.
            
        Returns:
            Respuesta de la API o un generador si stream=True.
            
        Raises:
            APIError: Si hay un error en la API.
        """
        # Determinar endpoint y payload según la API
        if self.api_name.lower() == "anthropic":
            url = f"{self.base_url}/v1/messages"
            payload = self._format_anthropic_payload(messages, model)
            # Anthropic streaming requiere un manejo diferente, por ahora no lo implementamos aquí
            if stream:
                payload["stream"] = True
        else:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }

        try:
            # Configurar timeouts optimizados
            if is_termux():
                timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)
            else:
                timeout = REQUEST_TIMEOUT
            
            response = self.session.post(
                url, 
                json=payload, 
                timeout=timeout,
                stream=stream  # Importante para streaming
            )

            if not stream:
                if response.status_code == 200:
                    api_response = response.json()
                    if self.api_name.lower() == "anthropic":
                        return self._normalize_anthropic_response(api_response)
                    return api_response
                else:
                    self._handle_api_error(response)
            else:
                # Si es streaming, devolvemos el generador
                if response.status_code == 200:
                    return self._stream_generator(response)
                else:
                    self._handle_api_error(response)

        except requests.exceptions.Timeout:
            error_msg = f"Timeout: La solicitud a {self.api_name} tardó demasiado tiempo"
            if is_termux():
                error_msg += "\n📱 Consejo: En móviles, las conexiones pueden ser más lentas. Intenta de nuevo."
            raise APIError(error_msg, api_name=self.api_name)
        except requests.exceptions.ConnectionError:
            error_msg = f"Error de conexión: No se pudo conectar a {self.api_name}"
            if is_termux():
                error_msg += "\n📱 Verifica tu conexión a internet y que tengas datos móviles o WiFi activo."
            raise APIError(error_msg, api_name=self.api_name)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de solicitud a {self.api_name}: {str(e)}"
            if is_termux():
                error_msg += "\n📱 Si el problema persiste, intenta cambiar de red o reiniciar la aplicación."
            raise APIError(error_msg, api_name=self.api_name)

    def _handle_api_error(self, response):
        """Maneja los errores de la API y lanza una APIError."""
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

    def _stream_generator(self, response):
        """Generador para procesar respuestas en streaming.
        Optimizado para conexiones móviles lentas.
        """
        chunk_size = MOBILE_NETWORK_CONFIG['chunk_size'] if is_termux() else 8192
        
        for line in response.iter_lines(chunk_size=chunk_size):
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[len('data: '):]
                    if json_str.strip() == '[DONE]':
                        break
                    try:
                        chunk = json.loads(json_str)
                        yield chunk
                        
                        # Añadir pequeña pausa en móviles para evitar saturar la conexión
                        if is_termux():
                            time.sleep(0.01)
                            
                    except json.JSONDecodeError:
                        # Ignorar líneas que no son JSON válido
                        continue
    
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
