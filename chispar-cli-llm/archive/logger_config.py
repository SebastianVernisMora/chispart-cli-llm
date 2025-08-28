"""
Configuración de logging para la aplicación CLI Universal para LLMs
Implementa mejores prácticas de logging con rotación, niveles y formateo estructurado
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
import json
from typing import Dict, Any, Optional

class StructuredFormatter(logging.Formatter):
    """
    Formateador personalizado que genera logs en formato JSON estructurado
    para facilitar el análisis y monitoreo
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Crear estructura base del log
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información adicional si está disponible
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'api_name'):
            log_entry['api_name'] = record.api_name
        if hasattr(record, 'model_name'):
            log_entry['model_name'] = record.model_name
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time_ms'] = record.execution_time
        if hasattr(record, 'tokens_used'):
            log_entry['tokens_used'] = record.tokens_used
        if hasattr(record, 'error_code'):
            log_entry['error_code'] = record.error_code
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredConsoleFormatter(logging.Formatter):
    """
    Formateador para consola con colores para mejor legibilidad
    """
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Aplicar color según el nivel
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formatear mensaje con color
        record.levelname = f"{color}{record.levelname}{reset}"
        
        # Formato legible para consola
        formatted = f"{color}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{reset} "
        formatted += f"{record.levelname} "
        formatted += f"{color}{record.name}{reset} - "
        formatted += f"{record.getMessage()}"
        
        # Agregar información adicional si está disponible
        extras = []
        if hasattr(record, 'api_name'):
            extras.append(f"api={record.api_name}")
        if hasattr(record, 'model_name'):
            extras.append(f"model={record.model_name}")
        if hasattr(record, 'execution_time'):
            extras.append(f"time={record.execution_time}ms")
        if hasattr(record, 'tokens_used'):
            extras.append(f"tokens={record.tokens_used}")
        
        if extras:
            formatted += f" [{', '.join(extras)}]"
        
        return formatted

def setup_logging(
    app_name: str = "llm_cli",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    structured_logs: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging con las mejores prácticas
    
    Args:
        app_name: Nombre de la aplicación para los logs
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio donde guardar los archivos de log
        max_file_size: Tamaño máximo de archivo antes de rotar (bytes)
        backup_count: Número de archivos de backup a mantener
        enable_console: Habilitar logging en consola
        enable_file: Habilitar logging en archivo
        structured_logs: Usar formato JSON estructurado para archivos
    
    Returns:
        Logger configurado
    """
    
    # Crear directorio de logs si no existe
    if enable_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar logger principal
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para consola
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredConsoleFormatter()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Handler para archivo principal con rotación
    if enable_file:
        log_file = os.path.join(log_dir, f"{app_name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        if structured_logs:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Handler separado para errores
    if enable_file:
        error_log_file = os.path.join(log_dir, f"{app_name}_errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        if structured_logs:
            error_formatter = StructuredFormatter()
        else:
            error_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
            )
        
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
    
    # Handler para métricas y auditoría
    if enable_file:
        audit_log_file = os.path.join(log_dir, f"{app_name}_audit.log")
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.addFilter(lambda record: hasattr(record, 'audit'))
        audit_formatter = StructuredFormatter()
        audit_handler.setFormatter(audit_formatter)
        logger.addHandler(audit_handler)
    
    # Evitar propagación a loggers padre
    logger.propagate = False
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger hijo con el nombre especificado
    
    Args:
        name: Nombre del logger (se agregará como sufijo al logger principal)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(f"llm_cli.{name}")

class LoggerMixin:
    """
    Mixin para agregar capacidades de logging a cualquier clase
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Obtiene el logger para esta clase"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
    
    def log_api_call(self, api_name: str, model_name: str, 
                     execution_time: float, tokens_used: Optional[int] = None,
                     request_id: Optional[str] = None):
        """
        Log específico para llamadas a APIs
        
        Args:
            api_name: Nombre de la API utilizada
            model_name: Nombre del modelo utilizado
            execution_time: Tiempo de ejecución en milisegundos
            tokens_used: Número de tokens utilizados
            request_id: ID único de la solicitud
        """
        self.logger.info(
            f"API call completed: {api_name}/{model_name}",
            extra={
                'audit': True,
                'api_name': api_name,
                'model_name': model_name,
                'execution_time': execution_time,
                'tokens_used': tokens_used,
                'request_id': request_id
            }
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None,
                  error_code: Optional[str] = None):
        """
        Log específico para errores con contexto adicional
        
        Args:
            error: Excepción ocurrida
            context: Contexto adicional del error
            error_code: Código de error personalizado
        """
        extra = {
            'error_code': error_code or type(error).__name__
        }
        
        if context:
            extra.update(context)
        
        self.logger.error(
            f"Error occurred: {str(error)}",
            exc_info=True,
            extra=extra
        )
    
    def log_user_action(self, action: str, user_id: Optional[str] = None,
                       session_id: Optional[str] = None, **kwargs):
        """
        Log específico para acciones de usuario (auditoría)
        
        Args:
            action: Descripción de la acción realizada
            user_id: ID del usuario (si está disponible)
            session_id: ID de la sesión
            **kwargs: Parámetros adicionales
        """
        extra = {
            'audit': True,
            'user_id': user_id,
            'session_id': session_id
        }
        extra.update(kwargs)
        
        self.logger.info(
            f"User action: {action}",
            extra=extra
        )

# Configuración por defecto
def init_default_logging():
    """Inicializa el logging con configuración por defecto"""
    return setup_logging(
        app_name="llm_cli",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_dir=os.getenv("LOG_DIR", "logs"),
        enable_console=True,
        enable_file=True,
        structured_logs=True
    )

# Logger principal de la aplicación
main_logger = init_default_logging()
