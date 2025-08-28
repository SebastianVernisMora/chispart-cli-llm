"""
Sistema Avanzado de Gestión de API Keys para Chispart Mobile
Maneja el almacenamiento seguro, validación y rotación de claves API
Optimizado para dispositivos móviles y Termux, con encriptación opcional.
"""

import os
import json
import hashlib
import base64
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
from pathlib import Path

# --- Encriptación Opcional ---
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("⚠️  Advertencia: La librería 'cryptography' no está instalada.")
    print("   Las claves API se guardarán ofuscadas en base64 en lugar de encriptadas.")
    print("   Para mayor seguridad, instala 'cryptography' con: pip install cryptography")

class APIKeyManager:
    """
    Gestor avanzado de API Keys con encriptación opcional, validación y almacenamiento seguro.
    """

    def __init__(self, storage_path: str = None, master_password: str = None):
        """
        Inicializa el gestor de API Keys.
        """
        self.storage_path = storage_path or self._get_default_storage_path()
        self.master_password = master_password
        self._cipher_suite = None
        self._api_keys = {}
        self._validation_cache = {}
        self._load_keys()

    def _get_default_storage_path(self) -> str:
        """Obtiene la ruta por defecto para almacenar las claves."""
        try:
            from termux_utils import get_termux_config_dir, is_termux
            if is_termux():
                config_dir = get_termux_config_dir()
            else:
                config_dir = os.path.expanduser("~/.config/chispart-mobile")
        except ImportError:
            config_dir = os.path.expanduser("~/.config/chispart-mobile")

        os.makedirs(config_dir, exist_ok=True)
        # Cambiar la extensión del archivo para reflejar su estado (encriptado o no)
        ext = ".enc" if ENCRYPTION_AVAILABLE else ".json.b64"
        return os.path.join(config_dir, "api_keys" + ext)

    def _derive_key(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """Deriva una clave de encriptación desde una contraseña."""
        if not ENCRYPTION_AVAILABLE:
            raise RuntimeError("La encriptación no está disponible.")

        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    def _get_cipher_suite(self) -> Optional['Fernet']:
        """Obtiene o crea el conjunto de cifrado."""
        if not ENCRYPTION_AVAILABLE:
            return None

        if self._cipher_suite is None:
            if self.master_password:
                key, _ = self._derive_key(self.master_password)
            else:
                device_id = self._get_device_identifier()
                key, _ = self._derive_key(device_id)
            self._cipher_suite = Fernet(key)
        return self._cipher_suite

    def _get_device_identifier(self) -> str:
        """Genera un identificador único del dispositivo para encriptación."""
        try:
            identifiers = []
            import uuid
            identifiers.append(str(uuid.getnode()))
            import platform
            identifiers.extend([platform.machine(), platform.processor(), platform.system()])
            termux_id = os.environ.get("PREFIX", "")
            if termux_id:
                identifiers.append(termux_id)
            if not identifiers:
                identifiers = ["chispart-mobile-default"]
            combined = "".join(identifiers)
            return hashlib.sha256(combined.encode()).hexdigest()[:32]
        except Exception:
            return "chispart-mobile-fallback-key-2024"

    def _load_keys(self):
        """Carga las claves API desde el almacenamiento."""
        if not os.path.exists(self.storage_path):
            self._api_keys = {}
            return

        try:
            with open(self.storage_path, "rb") as f:
                raw_data = f.read()

            if ENCRYPTION_AVAILABLE:
                cipher = self._get_cipher_suite()
                decrypted_data = cipher.decrypt(raw_data)
                self._api_keys = json.loads(decrypted_data.decode())
            else:
                # Cargar desde base64
                decoded_data = base64.b64decode(raw_data)
                self._api_keys = json.loads(decoded_data.decode())

        except Exception as e:
            print(f"⚠️  Error cargando claves API: {e}")
            print("   Se creará un nuevo almacén de claves.")
            self._api_keys = {}

    def _save_keys(self):
        """Guarda las claves API en el almacenamiento."""
        try:
            data_to_save = json.dumps(self._api_keys, indent=2).encode()

            if ENCRYPTION_AVAILABLE:
                cipher = self._get_cipher_suite()
                final_data = cipher.encrypt(data_to_save)
            else:
                # Guardar como base64
                final_data = base64.b64encode(data_to_save)

            temp_path = self.storage_path + ".tmp"
            with open(temp_path, "wb") as f:
                f.write(final_data)

            os.replace(temp_path, self.storage_path)
            os.chmod(self.storage_path, 0o600)

        except Exception as e:
            print(f"❌ Error guardando claves API: {e}")
            raise

    def set_api_key(self, provider: str, api_key: str, metadata: Dict = None) -> bool:
        """Establece una clave API para un proveedor."""
        try:
            if not api_key or len(api_key.strip()) < 3:
                raise ValueError("La clave API parece ser inválida")

            key_entry = {
                "key": api_key.strip(),
                "created_at": datetime.now().isoformat(),
                "last_validated": None,
                "validation_status": "pending",
                "usage_count": 0,
                "metadata": metadata or {},
            }
            self._api_keys[provider] = key_entry
            self._save_keys()
            if provider in self._validation_cache:
                del self._validation_cache[provider]
            return True
        except Exception as e:
            print(f"❌ Error estableciendo clave API para {provider}: {e}")
            return False

    def get_api_key(self, provider: str) -> Optional[str]:
        """Obtiene una clave API para un proveedor."""
        key_entry = self._api_keys.get(provider)
        if key_entry:
            key_entry["usage_count"] = key_entry.get("usage_count", 0) + 1
            # No guardamos en cada get para evitar escrituras constantes
            return key_entry["key"]

        env_vars = {
            "blackbox": ["BLACKBOX_API_KEY", "CHISPART_API_KEY"],
            "openai": ["OPENAI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"],
            "groq": ["GROQ_API_KEY"],
            "together": ["TOGETHER_API_KEY"],
        }
        for env_var in env_vars.get(provider, []):
            key = os.getenv(env_var)
            if key:
                self.set_api_key(provider, key, {"source": "environment"})
                return key
        return None

    # ... (el resto de los métodos como list_providers, remove_api_key, validate_api_key, etc., no necesitan cambios)
    # ... (They can remain as they are, since they call the modified get/set/save methods)
    def list_providers(self) -> List[Dict]:
        """
        Lista todos los proveedores configurados

        Returns:
            Lista de diccionarios con información de proveedores
        """
        providers = []
        for provider, key_entry in self._api_keys.items():
            providers.append(
                {
                    "provider": provider,
                    "created_at": key_entry.get("created_at"),
                    "last_validated": key_entry.get("last_validated"),
                    "validation_status": key_entry.get("validation_status", "unknown"),
                    "usage_count": key_entry.get("usage_count", 0),
                    "key_preview": (
                        key_entry["key"][:8] + "..." + key_entry["key"][-4:]
                        if len(key_entry["key"]) > 12
                        else "***"
                    ),
                    "metadata": key_entry.get("metadata", {}),
                }
            )
        return providers

    def remove_api_key(self, provider: str) -> bool:
        """
        Elimina una clave API

        Args:
            provider: Nombre del proveedor

        Returns:
            True si se eliminó correctamente
        """
        if provider in self._api_keys:
            del self._api_keys[provider]
            self._save_keys()

            # Limpiar caché
            if provider in self._validation_cache:
                del self._validation_cache[provider]

            return True
        return False

    async def validate_api_key(
        self, provider: str, force_refresh: bool = False
    ) -> Dict:
        """
        Valida una clave API haciendo una llamada de prueba

        Args:
            provider: Nombre del proveedor
            force_refresh: Forzar validación aunque esté en caché

        Returns:
            Diccionario con resultado de validación
        """
        # Verificar caché si no se fuerza refresh
        if not force_refresh and provider in self._validation_cache:
            cache_entry = self._validation_cache[provider]
            cache_time = datetime.fromisoformat(cache_entry["timestamp"])
            if datetime.now() - cache_time < timedelta(hours=1):
                return cache_entry["result"]

        api_key = self.get_api_key(provider)
        if not api_key:
            result = {"valid": False, "error": "No API key found", "provider": provider}
            return result

        # Configuraciones de validación por proveedor
        validation_configs = {
            "blackbox": {
                "url": "https://api.blackbox.ai/chat/completions",
                "headers": {"Authorization": f"Bearer {api_key}"},
                "payload": {
                    "model": "blackboxai/openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                },
            },
            "openai": {
                "url": "https://api.openai.com/v1/models",
                "headers": {"Authorization": f"Bearer {api_key}"},
            },
            "anthropic": {
                "url": "https://api.anthropic.com/v1/messages",
                "headers": {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                "payload": {
                    "model": "claude-3-haiku-20240307",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                },
            },
        }

        config = validation_configs.get(provider)
        if not config:
            result = {
                "valid": False,
                "error": f"Validation not implemented for {provider}",
                "provider": provider,
            }
            return result

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                if "payload" in config:
                    async with session.post(
                        config["url"], headers=config["headers"], json=config["payload"]
                    ) as response:
                        valid = response.status in [200, 201]
                        error = None if valid else f"HTTP {response.status}"
                else:
                    async with session.get(
                        config["url"], headers=config["headers"]
                    ) as response:
                        valid = response.status == 200
                        error = None if valid else f"HTTP {response.status}"

                result = {
                    "valid": valid,
                    "error": error,
                    "provider": provider,
                    "validated_at": datetime.now().isoformat(),
                }

                # Actualizar estado en almacenamiento
                if provider in self._api_keys:
                    self._api_keys[provider]["last_validated"] = result["validated_at"]
                    self._api_keys[provider]["validation_status"] = (
                        "valid" if valid else "invalid"
                    )
                    self._save_keys()

                # Guardar en caché
                self._validation_cache[provider] = {
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }

                return result

        except Exception as e:
            result = {
                "valid": False,
                "error": str(e),
                "provider": provider,
                "validated_at": datetime.now().isoformat(),
            }

            # Actualizar estado en almacenamiento
            if provider in self._api_keys:
                self._api_keys[provider]["last_validated"] = result["validated_at"]
                self._api_keys[provider]["validation_status"] = "error"
                self._save_keys()

            return result

    async def validate_all_keys(self) -> Dict[str, Dict]:
        """
        Valida todas las claves API configuradas
        """
        tasks = []
        providers = list(self._api_keys.keys())

        for provider in providers:
            task = self.validate_api_key(provider, force_refresh=True)
            tasks.append((provider, task))

        results = {}
        for provider, task in tasks:
            try:
                result = await task
                results[provider] = result
            except Exception as e:
                results[provider] = {
                    "valid": False,
                    "error": str(e),
                    "provider": provider,
                }

        return results

    def export_keys(self, include_keys: bool = False) -> Dict:
        """
        Exporta configuración de claves (sin las claves reales por defecto)
        """
        export_data = {"exported_at": datetime.now().isoformat(), "providers": {}}

        for provider, key_entry in self._api_keys.items():
            provider_data = {
                "created_at": key_entry.get("created_at"),
                "last_validated": key_entry.get("last_validated"),
                "validation_status": key_entry.get("validation_status"),
                "usage_count": key_entry.get("usage_count", 0),
                "metadata": key_entry.get("metadata", {}),
            }

            if include_keys:
                provider_data["key"] = key_entry["key"]
            else:
                provider_data["key_preview"] = (
                    key_entry["key"][:8] + "..." + key_entry["key"][-4:]
                    if len(key_entry["key"]) > 12
                    else "***"
                )

            export_data["providers"][provider] = provider_data

        return export_data

    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas de uso de las API Keys
        """
        total_keys = len(self._api_keys)
        valid_keys = sum(
            1
            for entry in self._api_keys.values()
            if entry.get("validation_status") == "valid"
        )
        total_usage = sum(
            entry.get("usage_count", 0) for entry in self._api_keys.values()
        )

        return {
            "total_keys": total_keys,
            "valid_keys": valid_keys,
            "invalid_keys": total_keys - valid_keys,
            "total_usage": total_usage,
            "providers": list(self._api_keys.keys()),
            "storage_path": self.storage_path,
            "last_updated": max(
                (entry.get("created_at", "") for entry in self._api_keys.values()),
                default=None,
            ),
        }

# Instancia global para uso en la aplicación
api_key_manager = APIKeyManager()
