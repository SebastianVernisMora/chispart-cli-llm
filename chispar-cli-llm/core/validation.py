"""
Módulo de validación para Chispart CLI
Centraliza toda la lógica de validación
"""

import os
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from config_extended import AVAILABLE_APIS, get_api_config, get_available_models, VISION_SUPPORTED_APIS, PDF_SUPPORTED_APIS
from utils import is_supported_image, is_supported_pdf, validate_file_size, format_file_size

class ValidationError(Exception):
    """Excepción para errores de validación"""
    def __init__(self, message: str, suggestion: Optional[str] = None, error_code: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
        super().__init__(self.message)

class APIValidator:
    """Validador para APIs y configuraciones"""
    
    @staticmethod
    def validate_api_key(api_name: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Valida que la clave API esté configurada correctamente
        
        Returns:
            Tuple[bool, Optional[config], Optional[error_message]]
        """
        if api_name not in AVAILABLE_APIS:
            return False, None, f"API '{api_name}' no está soportada"
        
        try:
            config = get_api_config(api_name)
            
            if not config["api_key"] or config["api_key"] == "your_api_key_here":
                api_info = AVAILABLE_APIS[api_name]
                error_msg = f"Clave API no configurada para {config['name']}"
                suggestion = f"Configura tu clave API como variable de entorno {api_info['default_key_env']} o usa 'chispart configure'"
                return False, None, f"{error_msg}. {suggestion}"
            
            return True, config, None
            
        except Exception as e:
            return False, None, f"Error al validar configuración de API: {str(e)}"
    
    @staticmethod
    def validate_api_support(api_name: str, feature: str) -> Tuple[bool, Optional[str]]:
        """
        Valida si una API soporta una característica específica
        
        Args:
            api_name: Nombre de la API
            feature: 'vision' o 'pdf'
            
        Returns:
            Tuple[bool, Optional[error_message]]
        """
        if feature == "vision":
            if api_name not in VISION_SUPPORTED_APIS:
                supported_apis = ", ".join(VISION_SUPPORTED_APIS)
                return False, f"La API {api_name} no soporta análisis de imágenes. APIs compatibles: {supported_apis}"
        
        elif feature == "pdf":
            if api_name not in PDF_SUPPORTED_APIS:
                supported_apis = ", ".join(PDF_SUPPORTED_APIS)
                return False, f"La API {api_name} no soporta análisis de PDFs. APIs compatibles: {supported_apis}"
        
        return True, None

class ModelValidator:
    """Validador para modelos de IA"""
    
    @staticmethod
    def validate_model(api_name: str, model: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Valida y obtiene el modelo a usar
        
        Args:
            api_name: Nombre de la API
            model: Modelo especificado (opcional)
            
        Returns:
            Tuple[bool, model_name, Optional[error_message]]
        """
        try:
            available_models = get_available_models(api_name)
            
            if not model:
                # Usar modelo por defecto
                from config_extended import get_default_model
                default_model = get_default_model(api_name)
                return True, default_model, None
            
            if model not in available_models:
                available_list = ", ".join(available_models.keys())
                error_msg = f"Modelo '{model}' no disponible para {api_name}"
                suggestion = f"Modelos disponibles: {available_list}"
                return False, model, f"{error_msg}. {suggestion}"
            
            return True, model, None
            
        except Exception as e:
            return False, model or "unknown", f"Error al validar modelo: {str(e)}"
    
    @staticmethod
    def get_optimal_model(api_name: str, task_type: str = "chat") -> str:
        """
        Obtiene el modelo óptimo para un tipo de tarea
        
        Args:
            api_name: Nombre de la API
            task_type: 'chat', 'vision', 'pdf', etc.
            
        Returns:
            Nombre del modelo óptimo
        """
        available_models = get_available_models(api_name)
        
        # Modelos preferidos por tarea
        preferred_models = {
            "vision": ["gpt-4-vision", "gpt-4o", "claude-3.5-sonnet"],
            "pdf": ["gpt-4", "gpt-4o", "claude-3.5-sonnet", "claude-3-opus"],
            "chat": ["gpt-4o", "gpt-4", "claude-3.5-sonnet", "llama-3.1-70b"],
            "code": ["gpt-4", "claude-3.5-sonnet", "deepseek-chat"]
        }
        
        # Buscar el primer modelo preferido disponible
        for preferred in preferred_models.get(task_type, preferred_models["chat"]):
            if preferred in available_models:
                return preferred
        
        # Si no hay preferidos, usar el por defecto
        from config_extended import get_default_model
        return get_default_model(api_name)

class FileValidator:
    """Validador para archivos"""
    
    @staticmethod
    def validate_file_exists(file_path: str) -> Tuple[bool, Optional[str]]:
        """Valida que un archivo exista"""
        if not os.path.exists(file_path):
            suggestion = "Verifica la ruta del archivo y que tengas permisos de lectura"
            return False, f"El archivo '{file_path}' no existe. {suggestion}"
        
        if not os.path.isfile(file_path):
            return False, f"'{file_path}' no es un archivo válido"
        
        return True, None
    
    @staticmethod
    def validate_image_file(file_path: str, max_size_mb: int = 20) -> Tuple[bool, Optional[str]]:
        """Valida un archivo de imagen"""
        # Verificar existencia
        exists, error = FileValidator.validate_file_exists(file_path)
        if not exists:
            return False, error
        
        # Verificar formato
        if not is_supported_image(file_path):
            return False, "Formato de imagen no soportado. Formatos válidos: jpg, jpeg, png, webp"
        
        # Verificar tamaño
        if not validate_file_size(file_path, max_size_mb):
            actual_size = format_file_size(os.path.getsize(file_path))
            return False, f"Archivo demasiado grande ({actual_size}). Máximo permitido: {max_size_mb}MB"
        
        return True, None
    
    @staticmethod
    def validate_pdf_file(file_path: str, max_size_mb: int = 20) -> Tuple[bool, Optional[str]]:
        """Valida un archivo PDF"""
        # Verificar existencia
        exists, error = FileValidator.validate_file_exists(file_path)
        if not exists:
            return False, error
        
        # Verificar formato
        if not is_supported_pdf(file_path):
            return False, "El archivo debe ser un PDF válido"
        
        # Verificar tamaño
        if not validate_file_size(file_path, max_size_mb):
            actual_size = format_file_size(os.path.getsize(file_path))
            return False, f"Archivo demasiado grande ({actual_size}). Máximo permitido: {max_size_mb}MB"
        
        return True, None
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Obtiene información detallada de un archivo"""
        if not os.path.exists(file_path):
            return {"exists": False}
        
        stat = os.stat(file_path)
        file_info = {
            "exists": True,
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "extension": Path(file_path).suffix.lower(),
            "name": os.path.basename(file_path),
            "is_image": is_supported_image(file_path),
            "is_pdf": is_supported_pdf(file_path)
        }
        
        return file_info

class InputValidator:
    """Validador para inputs de usuario"""
    
    @staticmethod
    def validate_message(message: str, min_length: int = 1, max_length: int = 50000) -> Tuple[bool, Optional[str]]:
        """Valida un mensaje de texto"""
        if not message or not message.strip():
            return False, "El mensaje no puede estar vacío"
        
        message = message.strip()
        
        if len(message) < min_length:
            return False, f"El mensaje debe tener al menos {min_length} caracteres"
        
        if len(message) > max_length:
            return False, f"El mensaje es demasiado largo. Máximo: {max_length} caracteres"
        
        return True, None
    
    @staticmethod
    def validate_prompt(prompt: str, context: str = "general") -> Tuple[bool, str, Optional[str]]:
        """
        Valida y optimiza un prompt según el contexto
        
        Args:
            prompt: Prompt original
            context: Contexto ('image', 'pdf', 'chat', etc.)
            
        Returns:
            Tuple[bool, optimized_prompt, Optional[error_message]]
        """
        valid, error = InputValidator.validate_message(prompt)
        if not valid:
            return False, prompt, error
        
        # Optimizaciones por contexto
        optimized_prompt = prompt.strip()
        
        if context == "image" and len(optimized_prompt) < 10:
            # Mejorar prompts muy cortos para imágenes
            if optimized_prompt.lower() in ["que es", "que hay", "describe"]:
                optimized_prompt = "Describe detalladamente lo que ves en esta imagen"
        
        elif context == "pdf" and len(optimized_prompt) < 15:
            # Mejorar prompts muy cortos para PDFs
            if optimized_prompt.lower() in ["resume", "resumen", "que dice"]:
                optimized_prompt = "Resume los puntos principales de este documento"
        
        return True, optimized_prompt, None

class ConfigValidator:
    """Validador para configuraciones"""
    
    @staticmethod
    def validate_env_file(env_path: str = ".env") -> Tuple[bool, List[str], List[str]]:
        """
        Valida un archivo .env
        
        Returns:
            Tuple[bool, configured_apis, missing_apis]
        """
        configured_apis = []
        missing_apis = []
        
        if not os.path.exists(env_path):
            return False, configured_apis, list(AVAILABLE_APIS.keys())
        
        try:
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            for api_key, api_info in AVAILABLE_APIS.items():
                env_var = api_info['default_key_env']
                
                # Buscar la variable en el archivo
                if f"{env_var}=" in env_content:
                    # Verificar que no esté vacía
                    lines = env_content.split('\n')
                    for line in lines:
                        if line.startswith(f"{env_var}="):
                            value = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if value and value != "your_api_key_here":
                                configured_apis.append(api_key)
                            else:
                                missing_apis.append(api_key)
                            break
                else:
                    missing_apis.append(api_key)
            
            return len(configured_apis) > 0, configured_apis, missing_apis
            
        except Exception as e:
            return False, [], list(AVAILABLE_APIS.keys())
    
    @staticmethod
    def validate_termux_environment() -> Dict[str, Any]:
        """Valida el entorno Termux"""
        validation_result = {
            "is_termux": False,
            "storage_setup": False,
            "dependencies": {},
            "recommendations": []
        }
        
        try:
            from termux_utils import is_termux, check_termux_dependencies
            
            validation_result["is_termux"] = is_termux()
            
            if validation_result["is_termux"]:
                # Verificar setup de storage
                storage_path = os.path.expanduser("~/storage/shared")
                validation_result["storage_setup"] = os.path.exists(storage_path)
                
                if not validation_result["storage_setup"]:
                    validation_result["recommendations"].append(
                        "Ejecuta 'termux-setup-storage' para acceder a archivos del teléfono"
                    )
                
                # Verificar dependencias
                validation_result["dependencies"] = check_termux_dependencies()
                
                missing_deps = [dep for dep, available in validation_result["dependencies"].items() if not available]
                if missing_deps:
                    validation_result["recommendations"].append(
                        f"Instala dependencias faltantes: pip install {' '.join(missing_deps)}"
                    )
        
        except ImportError:
            pass
        
        return validation_result

# Funciones de conveniencia
def validate_complete_request(api_name: str, model: Optional[str] = None, message: Optional[str] = None, 
                            file_path: Optional[str] = None, file_type: Optional[str] = None) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validación completa de una request
    
    Returns:
        Tuple[bool, validation_data, Optional[error_message]]
    """
    validation_data = {}
    
    # Validar API
    api_valid, config, api_error = APIValidator.validate_api_key(api_name)
    if not api_valid:
        return False, {}, api_error
    validation_data["config"] = config
    
    # Validar modelo
    model_valid, validated_model, model_error = ModelValidator.validate_model(api_name, model)
    if not model_valid:
        return False, validation_data, model_error
    validation_data["model"] = validated_model
    
    # Validar mensaje si se proporciona
    if message:
        msg_valid, msg_error = InputValidator.validate_message(message)
        if not msg_valid:
            return False, validation_data, msg_error
        validation_data["message"] = message.strip()
    
    # Validar archivo si se proporciona
    if file_path:
        if file_type == "image":
            # Validar soporte de visión
            vision_valid, vision_error = APIValidator.validate_api_support(api_name, "vision")
            if not vision_valid:
                return False, validation_data, vision_error
            
            # Validar archivo de imagen
            file_valid, file_error = FileValidator.validate_image_file(file_path)
            if not file_valid:
                return False, validation_data, file_error
                
        elif file_type == "pdf":
            # Validar soporte de PDF
            pdf_valid, pdf_error = APIValidator.validate_api_support(api_name, "pdf")
            if not pdf_valid:
                return False, validation_data, pdf_error
            
            # Validar archivo PDF
            file_valid, file_error = FileValidator.validate_pdf_file(file_path)
            if not file_valid:
                return False, validation_data, file_error
        
        validation_data["file_path"] = file_path
        validation_data["file_info"] = FileValidator.get_file_info(file_path)
    
    return True, validation_data, None
