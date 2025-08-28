"""
Gestor de configuración avanzado para Chispart CLI Modern
Maneja configuración jerárquica, validación y persistencia
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

from config_extended import AVAILABLE_APIS, DEFAULT_API, DEFAULT_MODELS


class ConfigManager:
    """Gestor avanzado de configuración del sistema"""
    
    def __init__(self):
        self.config_dir = Path.cwd()
        self.env_file = self.config_dir / ".env"
        self.config_file = self.config_dir / "chispart_config.json"
        self.user_config = {}
        
        # Cargar configuración
        self._load_environment()
        self._load_user_config()
    
    def _load_environment(self):
        """Carga variables de entorno desde .env"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
    
    def _load_user_config(self):
        """Carga configuración de usuario desde JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.user_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.user_config = {}
        else:
            self.user_config = self._get_default_user_config()
    
    def _get_default_user_config(self) -> Dict[str, Any]:
        """Obtiene configuración de usuario por defecto"""
        return {
            "version": "2.0.0",
            "default_api": DEFAULT_API,
            "theme": "chispart_neon",
            "ui_preferences": {
                "show_banners": True,
                "compact_mode": False,
                "auto_save_history": True,
                "streaming_enabled": True
            },
            "api_preferences": {
                "timeout_multiplier": 1.0,
                "retry_attempts": 3,
                "default_models": DEFAULT_MODELS.copy()
            },
            "file_handling": {
                "max_image_size_mb": 20,
                "max_pdf_size_mb": 20,
                "auto_cleanup_temp": True
            }
        }
    
    def save_user_config(self) -> bool:
        """Guarda configuración de usuario"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """
        Obtiene configuración completa de una API
        
        Args:
            api_name: Nombre de la API
            
        Returns:
            Dict con configuración de la API
        """
        if api_name not in AVAILABLE_APIS:
            api_name = DEFAULT_API
        
        base_config = AVAILABLE_APIS[api_name].copy()
        
        # Obtener clave API desde variables de entorno
        api_key = self._get_api_key(api_name)
        
        # Combinar con preferencias de usuario
        user_prefs = self.user_config.get("api_preferences", {})
        
        return {
            "name": base_config["name"],
            "base_url": base_config["base_url"],
            "api_key": api_key,
            "timeout_multiplier": user_prefs.get("timeout_multiplier", 1.0),
            "retry_attempts": user_prefs.get("retry_attempts", 3),
            "default_model": user_prefs.get("default_models", {}).get(api_name, DEFAULT_MODELS.get(api_name))
        }
    
    def _get_api_key(self, api_name: str) -> str:
        """Obtiene clave API desde variables de entorno"""
        if api_name not in AVAILABLE_APIS:
            return ""
        
        env_var = AVAILABLE_APIS[api_name]["default_key_env"]
        
        # Compatibilidad especial para chispart/blackbox
        if api_name == "chispart":
            return (os.getenv("CHISPART_API_KEY") or 
                   os.getenv("BLACKBOX_API_KEY") or 
                   AVAILABLE_APIS[api_name].get("default_key", ""))
        
        return os.getenv(env_var, AVAILABLE_APIS[api_name].get("default_key", ""))
    
    def set_api_key(self, api_name: str, api_key: str) -> bool:
        """
        Establece clave API en variables de entorno
        
        Args:
            api_name: Nombre de la API
            api_key: Clave API
            
        Returns:
            True si se guardó exitosamente
        """
        if api_name not in AVAILABLE_APIS:
            return False
        
        env_var = AVAILABLE_APIS[api_name]["default_key_env"]
        
        try:
            # Crear archivo .env si no existe
            if not self.env_file.exists():
                self.env_file.touch()
            
            # Usar set_key para actualizar/agregar la variable
            set_key(str(self.env_file), env_var, api_key)
            
            # Recargar variables de entorno
            load_dotenv(self.env_file, override=True)
            
            return True
        except Exception:
            return False
    
    def get_configured_apis(self) -> List[str]:
        """Obtiene lista de APIs configuradas"""
        configured = []
        for api_name in AVAILABLE_APIS.keys():
            if self._get_api_key(api_name):
                configured.append(api_name)
        return configured
    
    def is_api_configured(self, api_name: str) -> bool:
        """Verifica si una API está configurada"""
        return bool(self._get_api_key(api_name))
    
    def get_default_api(self) -> str:
        """Obtiene API por defecto"""
        return self.user_config.get("default_api", DEFAULT_API)
    
    def set_default_api(self, api_name: str) -> bool:
        """Establece API por defecto"""
        if api_name in AVAILABLE_APIS:
            self.user_config["default_api"] = api_name
            return self.save_user_config()
        return False
    
    def get_theme(self) -> str:
        """Obtiene tema actual"""
        return self.user_config.get("theme", "chispart_neon")
    
    def set_theme(self, theme_name: str) -> bool:
        """Establece tema"""
        self.user_config["theme"] = theme_name
        return self.save_user_config()
    
    def get_ui_preference(self, key: str, default: Any = None) -> Any:
        """Obtiene preferencia de UI"""
        return self.user_config.get("ui_preferences", {}).get(key, default)
    
    def set_ui_preference(self, key: str, value: Any) -> bool:
        """Establece preferencia de UI"""
        if "ui_preferences" not in self.user_config:
            self.user_config["ui_preferences"] = {}
        
        self.user_config["ui_preferences"][key] = value
        return self.save_user_config()
    
    def get_api_preference(self, key: str, default: Any = None) -> Any:
        """Obtiene preferencia de API"""
        return self.user_config.get("api_preferences", {}).get(key, default)
    
    def set_api_preference(self, key: str, value: Any) -> bool:
        """Establece preferencia de API"""
        if "api_preferences" not in self.user_config:
            self.user_config["api_preferences"] = {}
        
        self.user_config["api_preferences"][key] = value
        return self.save_user_config()
    
    def get_file_handling_preference(self, key: str, default: Any = None) -> Any:
        """Obtiene preferencia de manejo de archivos"""
        return self.user_config.get("file_handling", {}).get(key, default)
    
    def set_file_handling_preference(self, key: str, value: Any) -> bool:
        """Establece preferencia de manejo de archivos"""
        if "file_handling" not in self.user_config:
            self.user_config["file_handling"] = {}
        
        self.user_config["file_handling"][key] = value
        return self.save_user_config()
    
    def reset_to_defaults(self) -> bool:
        """Resetea configuración a valores por defecto"""
        try:
            # Resetear configuración de usuario
            self.user_config = self._get_default_user_config()
            
            # Eliminar archivo de configuración existente
            if self.config_file.exists():
                self.config_file.unlink()
            
            # Guardar nueva configuración
            return self.save_user_config()
        except Exception:
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtiene información del sistema y configuración"""
        apis_status = {}
        for api_name in AVAILABLE_APIS.keys():
            apis_status[api_name] = self.is_api_configured(api_name)
        
        return {
            "default_api": self.get_default_api(),
            "current_theme": self.get_theme(),
            "config_dir": str(self.config_dir),
            "config_file": str(self.config_file),
            "env_file": str(self.env_file),
            "history_file": str(self.config_dir / "chat_history.json"),
            "apis_status": apis_status,
            "configured_apis_count": len(self.get_configured_apis()),
            "total_apis_count": len(AVAILABLE_APIS),
            "config_version": self.user_config.get("version", "unknown")
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Valida la configuración actual"""
        issues = []
        warnings = []
        
        # Verificar que al menos una API esté configurada
        configured_apis = self.get_configured_apis()
        if not configured_apis:
            issues.append("No hay APIs configuradas")
        
        # Verificar que la API por defecto esté configurada
        default_api = self.get_default_api()
        if default_api not in configured_apis:
            warnings.append(f"La API por defecto '{default_api}' no está configurada")
        
        # Verificar archivos de configuración
        if not self.env_file.exists():
            warnings.append("Archivo .env no existe")
        
        # Verificar permisos de escritura
        if not os.access(self.config_dir, os.W_OK):
            issues.append("No hay permisos de escritura en el directorio de configuración")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "configured_apis": configured_apis,
            "default_api": default_api
        }
    
    def export_config(self, include_api_keys: bool = False) -> Dict[str, Any]:
        """
        Exporta configuración para backup o migración
        
        Args:
            include_api_keys: Si incluir claves API (peligroso)
            
        Returns:
            Dict con configuración exportable
        """
        export_data = {
            "version": "2.0.0",
            "export_timestamp": str(Path.cwd()),
            "user_config": self.user_config.copy()
        }
        
        if include_api_keys:
            export_data["api_keys"] = {}
            for api_name in AVAILABLE_APIS.keys():
                api_key = self._get_api_key(api_name)
                if api_key:
                    export_data["api_keys"][api_name] = api_key
        
        return export_data
    
    def import_config(self, config_data: Dict[str, Any], 
                     import_api_keys: bool = False) -> bool:
        """
        Importa configuración desde backup
        
        Args:
            config_data: Datos de configuración
            import_api_keys: Si importar claves API
            
        Returns:
            True si se importó exitosamente
        """
        try:
            # Validar formato
            if "user_config" not in config_data:
                return False
            
            # Importar configuración de usuario
            self.user_config = config_data["user_config"]
            
            # Importar claves API si se solicita
            if import_api_keys and "api_keys" in config_data:
                for api_name, api_key in config_data["api_keys"].items():
                    self.set_api_key(api_name, api_key)
            
            # Guardar configuración
            return self.save_user_config()
            
        except Exception:
            return False


# Instancia global del gestor de configuración
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Obtiene instancia singleton del gestor de configuración"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
