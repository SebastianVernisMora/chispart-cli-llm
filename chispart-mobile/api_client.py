"""
Cliente Universal para APIs de LLM
Soporta múltiples proveedores: Blackbox, OpenAI, Anthropic, Groq, Together AI
"""

import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

try:
    import aiohttp
    import requests

    ASYNC_AVAILABLE = True
except ImportError:
    import requests

    ASYNC_AVAILABLE = False


class APIError(Exception):
    """Excepción personalizada para errores de API"""

    def __init__(
        self,
        message: str,
        api_name: str = None,
        status_code: int = None,
        response_data: dict = None,
    ):
        self.message = message
        self.api_name = api_name
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message)


class UniversalAPIClient:
    """
    Cliente universal para múltiples APIs de LLM
    Soporta: Blackbox AI, OpenAI, Anthropic, Groq, Together AI
    """

    def __init__(self, api_key: str, base_url: str, api_name: str = "unknown"):
        """
        Inicializa el cliente API

        Args:
            api_key: Clave de API
            base_url: URL base de la API
            api_name: Nombre del proveedor de API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.api_name = api_name
        self.session = None

        # Configuración de timeouts optimizada para móviles
        self.timeout_config = self._get_timeout_config()

        # Headers comunes
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": f"Chispart-Mobile/1.0 ({api_name})",
        }

        # Configurar headers específicos por API
        self._setup_api_headers()

    def _get_timeout_config(self) -> Dict[str, int]:
        """Obtiene configuración de timeouts optimizada"""
        try:
            from termux_utils import is_termux, get_mobile_optimized_timeouts

            if is_termux():
                return get_mobile_optimized_timeouts()
        except ImportError:
            pass

        # Configuración por defecto
        return {"connect_timeout": 10, "read_timeout": 60, "total_timeout": 120}

    def _setup_api_headers(self):
        """Configura headers específicos para cada API"""
        if self.api_name.lower() in ["blackbox", "chispart"]:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.api_name.lower() == "openai":
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.api_name.lower() == "anthropic":
            self.headers["x-api-key"] = self.api_key
            self.headers["anthropic-version"] = "2023-06-01"
        elif self.api_name.lower() in ["groq", "together"]:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            # Fallback genérico
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _get_chat_endpoint(self) -> str:
        """Obtiene el endpoint de chat según la API"""
        if self.api_name.lower() in ["blackbox", "chispart"]:
            return f"{self.base_url}/v1/chat/completions"
        elif self.api_name.lower() == "anthropic":
            return f"{self.base_url}/v1/messages"
        else:
            # OpenAI compatible (Groq, Together, etc.)
            return f"{self.base_url}/chat/completions"

    def _format_messages_for_api(self, messages: List[Dict]) -> Dict:
        """Formatea mensajes según el formato requerido por cada API"""
        if self.api_name.lower() == "anthropic":
            # Anthropic usa un formato diferente
            formatted_messages = []
            system_message = None

            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg["content"]
                else:
                    formatted_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            payload = {"messages": formatted_messages, "max_tokens": 4000}

            if system_message:
                payload["system"] = system_message

            return payload
        else:
            # Formato OpenAI compatible
            return {"messages": messages}

    def chat_completions(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """
        Envía una solicitud de chat completions

        Args:
            messages: Lista de mensajes en formato OpenAI
            model: Nombre del modelo a usar
            **kwargs: Parámetros adicionales

        Returns:
            Respuesta de la API

        Raises:
            APIError: Si hay un error en la API
        """
        endpoint = self._get_chat_endpoint()

        # Formatear payload según la API
        payload = self._format_messages_for_api(messages)
        payload["model"] = model

        # Parámetros adicionales comunes
        payload.update(
            {
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": kwargs.get("stream", False),
            }
        )

        # Parámetros específicos por API
        if self.api_name.lower() not in ["anthropic"]:
            payload.update(
                {
                    "top_p": kwargs.get("top_p", 1.0),
                    "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                    "presence_penalty": kwargs.get("presence_penalty", 0.0),
                }
            )

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=(
                    self.timeout_config["connect_timeout"],
                    self.timeout_config["read_timeout"],
                ),
            )

            # Verificar status code
            if response.status_code != 200:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass

                raise APIError(
                    message=f"HTTP {response.status_code}: {error_data.get('error', {}).get('message', response.text)}",
                    api_name=self.api_name,
                    status_code=response.status_code,
                    response_data=error_data,
                )

            return response.json()

        except requests.exceptions.Timeout:
            raise APIError(
                message=f"Timeout al conectar con {self.api_name}",
                api_name=self.api_name,
                status_code=408,
            )
        except requests.exceptions.ConnectionError:
            raise APIError(
                message=f"Error de conexión con {self.api_name}",
                api_name=self.api_name,
                status_code=503,
            )
        except requests.exceptions.RequestException as e:
            raise APIError(
                message=f"Error de red: {str(e)}",
                api_name=self.api_name,
                status_code=500,
            )
        except Exception as e:
            raise APIError(
                message=f"Error inesperado: {str(e)}",
                api_name=self.api_name,
                status_code=500,
            )

    def extract_response_content(self, response: Dict) -> str:
        """
        Extrae el contenido de texto de la respuesta

        Args:
            response: Respuesta de la API

        Returns:
            Contenido de texto extraído
        """
        try:
            if self.api_name.lower() == "anthropic":
                # Formato Anthropic
                if "content" in response and response["content"]:
                    return response["content"][0].get("text", "")
            else:
                # Formato OpenAI compatible
                if "choices" in response and response["choices"]:
                    choice = response["choices"][0]
                    if "message" in choice:
                        return choice["message"].get("content", "")
                    elif "text" in choice:
                        return choice["text"]

            return "No se pudo extraer el contenido de la respuesta"

        except Exception as e:
            return f"Error extrayendo contenido: {str(e)}"

    def get_usage_info(self, response: Dict) -> Optional[Dict]:
        """
        Extrae información de uso de tokens de la respuesta

        Args:
            response: Respuesta de la API

        Returns:
            Información de uso o None si no está disponible
        """
        try:
            if "usage" in response:
                return response["usage"]
            elif "meta" in response and "usage" in response["meta"]:
                # Algunos APIs usan 'meta'
                return response["meta"]["usage"]
            return None
        except:
            return None

    async def chat_completions_async(
        self, messages: List[Dict], model: str, **kwargs
    ) -> Dict:
        """
        Versión asíncrona de chat_completions

        Args:
            messages: Lista de mensajes
            model: Nombre del modelo
            **kwargs: Parámetros adicionales

        Returns:
            Respuesta de la API
        """
        if not ASYNC_AVAILABLE:
            raise APIError(
                message="aiohttp no está disponible para operaciones asíncronas",
                api_name=self.api_name,
            )

        endpoint = self._get_chat_endpoint()
        payload = self._format_messages_for_api(messages)
        payload["model"] = model
        payload.update(
            {
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": kwargs.get("stream", False),
            }
        )

        timeout = aiohttp.ClientTimeout(
            connect=self.timeout_config["connect_timeout"],
            total=self.timeout_config["total_timeout"],
        )

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint, headers=self.headers, json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise APIError(
                            message=f"HTTP {response.status}: {error_text}",
                            api_name=self.api_name,
                            status_code=response.status,
                        )

                    return await response.json()

        except asyncio.TimeoutError:
            raise APIError(
                message=f"Timeout al conectar con {self.api_name}",
                api_name=self.api_name,
                status_code=408,
            )
        except Exception as e:
            raise APIError(
                message=f"Error asíncrono: {str(e)}",
                api_name=self.api_name,
                status_code=500,
            )

    def validate_connection(self) -> Dict[str, Any]:
        """
        Valida la conexión con la API

        Returns:
            Diccionario con información de validación
        """
        try:
            # Mensaje de prueba simple
            test_messages = [{"role": "user", "content": "Hello"}]

            # Usar un modelo por defecto según la API
            default_models = {
                "blackbox": "blackboxai/openai/gpt-3.5-turbo",
                "chispart": "blackboxai/openai/gpt-3.5-turbo",
                "openai": "gpt-3.5-turbo",
                "anthropic": "claude-3-haiku-20240307",
                "groq": "llama3-8b-8192",
                "together": "meta-llama/Llama-2-7b-chat-hf",
            }

            model = default_models.get(self.api_name.lower(), "gpt-3.5-turbo")

            start_time = time.time()
            response = self.chat_completions(
                messages=test_messages, model=model, max_tokens=10
            )
            response_time = time.time() - start_time

            return {
                "valid": True,
                "response_time": response_time,
                "model_used": model,
                "api_name": self.api_name,
                "timestamp": datetime.now().isoformat(),
            }

        except APIError as e:
            return {
                "valid": False,
                "error": e.message,
                "status_code": e.status_code,
                "api_name": self.api_name,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error inesperado: {str(e)}",
                "api_name": self.api_name,
                "timestamp": datetime.now().isoformat(),
            }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            self.session.close()
