"""
""
Chispart Mobile - Aplicación Principal
Universal LLM Terminal optimizado para dispositivos móviles y Termux
Integra API Key Manager, PWA Manager y Config Manager
"""
import os
import sys
import json
import asyncio
import queue
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Flask y extensiones
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Sistemas core de Chispart Mobile
from core.api_key_manager import api_key_manager, APIKeyManager
from core.pwa_manager import pwa_manager, PWAManager
from core.config_manager import config_manager, ConfigLevel, ConfigScope

# Importar utilidades del proyecto
from api_client import UniversalAPIClient, APIError
from utils import (
    is_supported_image, is_supported_pdf, create_image_data_url,
    extract_text_from_pdf, save_conversation_history, load_conversation_history,
    format_file_size, validate_file_size
)
from termux_utils import is_termux, get_optimized_console_width, get_mobile_file_limits
from config_extended import (
    get_api_config, get_available_models, get_default_model,
    AVAILABLE_APIS, DEFAULT_API, get_vision_supported_apis, get_pdf_supported_apis,
    validate_api_model_combination, get_api_statistics
)
from core.shell import InteractiveShell
from core.analyzer import DirectoryAnalyzer

# Global queue for log streaming
log_queue = queue.Queue()

class ChispartMobileApp:
    """
    Aplicación principal de Chispart Mobile con arquitectura modular avanzada
    """
    
    def __init__(self):
        """Inicializa la aplicación con todos los sistemas integrados"""
        self.app = Flask(__name__)
        self.app.secret_key = self._generate_secret_key()
        
        # Configurar CORS para PWA
        CORS(self.app, origins=['*'])
        
        # Inicializar sistemas core
        self.api_manager = api_key_manager
        self.pwa_manager = pwa_manager
        self.config_manager = config_manager
        self.interactive_shell = InteractiveShell(log_queue=log_queue)
        
        # Configurar PWA con la app Flask
        self.pwa_manager.init_app(self.app)
        
        # Estado de la aplicación
        self.is_mobile = is_termux()
        self.upload_folder = self._setup_upload_folder()
        
        # Configurar aplicación
        self._configure_app()
        self._register_routes()
        self._setup_error_handlers()
        
        print(f"🚀 Chispart Mobile inicializado ({'Termux' if self.is_mobile else 'Desktop'})")
    
    def _generate_secret_key(self) -> str:
        """Genera una clave secreta para Flask"""
        try:
            # Intentar usar clave persistente
            key_file = Path(config_manager.config_dir) / 'flask_secret.key'
            if key_file.exists():
                return key_file.read_text().strip()
            else:
                # Generar nueva clave
                import secrets
                key = secrets.token_hex(32)
                key_file.write_text(key)
                os.chmod(key_file, 0o600)
                return key
        except Exception:
            # Fallback
            return 'chispart-mobile-fallback-key-2024'
    
    def _setup_upload_folder(self) -> str:
        """Configura directorio para uploads"""
        try:
            from termux_utils import get_termux_temp_dir
            upload_dir = os.path.join(get_termux_temp_dir(), 'uploads')
        except ImportError:
            upload_dir = os.path.join(os.getcwd(), 'uploads')
        
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    def _configure_app(self):
        """Configura la aplicación Flask"""
        # Configuración básica
        self.app.config.update({
            'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB max para móviles
            'UPLOAD_FOLDER': self.upload_folder,
            'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # 1 año para archivos estáticos
        })
        
        # Configuración específica para móviles
        if self.is_mobile:
            self.app.config.update({
                'MAX_CONTENT_LENGTH': 20 * 1024 * 1024,  # 20MB para móviles
                'TEMPLATES_AUTO_RELOAD': False,  # Desactivar para mejor rendimiento
            })
    
    def _register_routes(self):
        """Registra todas las rutas de la aplicación"""
        
        @self.app.route('/')
        def index():
            """Página principal de la aplicación"""
            return render_template('index.html', 
                                 is_mobile=self.is_mobile,
                                 config=self._get_client_config())
        
        @self.app.route('/chat')
        def chat_page():
            """Página de chat"""
            return render_template('chat.html',
                                 is_mobile=self.is_mobile,
                                 config=self._get_client_config())
        
        @self.app.route('/config')
        def config_page():
            """Página de configuración"""
            return render_template('config.html',
                                 is_mobile=self.is_mobile,
                                 config=self._get_client_config(),
                                 api_providers=self._get_api_providers_info())
        
        @self.app.route('/console')
        def console_page():
            """Página de la consola interactiva"""
            return render_template('console.html',
                                 is_mobile=self.is_mobile,
                                 config=self._get_client_config())

        # API Routes
        @self.app.route('/api/chat', methods=['POST'])
        def api_chat():
            """Endpoint principal para chat con IA"""
            try:
                data = request.get_json()
                message = data.get('message', '').strip()
                api_name = data.get('api', config_manager.get('default_api'))
                model = data.get('model', config_manager.get('default_model'))
                stream = data.get('stream', False)
                
                if not message:
                    return jsonify({'error': 'Mensaje vacío'}), 400
                
                # Obtener API key
                api_key = self.api_manager.get_api_key(api_name)
                if not api_key:
                    return jsonify({
                        'error': f'API key no configurada para {api_name}',
                        'requires_setup': True
                    }), 400
                
                # Validar API key si es necesario
                validation = asyncio.run(self.api_manager.validate_api_key(api_name))
                if not validation['valid']:
                    return jsonify({
                        'error': f'API key inválida para {api_name}: {validation["error"]}',
                        'requires_setup': True
                    }), 400
                
                # Crear cliente y enviar mensaje
                client = UniversalAPIClient(api_key, self._get_api_base_url(api_name), api_name)
                messages = [{"role": "user", "content": message}]
                
                if stream:
                    # Implementar streaming (placeholder)
                    return jsonify({'error': 'Streaming no implementado aún'}), 501
                else:
                    response = client.chat_completions(messages, model)
                    content = client.extract_response_content(response)
                    usage = client.get_usage_info(response)
                    
                    # Guardar en historial
                    conversation = {
                        "type": "mobile_chat",
                        "api": api_name,
                        "model": model,
                        "message": message,
                        "response": content,
                        "usage": usage,
                        "timestamp": datetime.now().isoformat()
                    }
                    save_conversation_history(conversation)
                    
                    return jsonify({
                        'response': content,
                        'model_used': model,
                        'api_used': api_name,
                        'usage': usage,
                        'timestamp': conversation['timestamp']
                    })
                    
            except APIError as e:
                return jsonify({
                    'error': f'Error de API: {e.message}',
                    'api_name': e.api_name,
                    'status_code': e.status_code
                }), 500
            except Exception as e:
                return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
        
        @self.app.route('/api/image', methods=['POST'])
        def api_image():
            """Endpoint para análisis de imágenes"""
            try:
                if 'image' not in request.files:
                    return jsonify({'error': 'No se proporcionó imagen'}), 400
                
                file = request.files['image']
                if file.filename == '':
                    return jsonify({'error': 'No se seleccionó archivo'}), 400
                
                # Parámetros
                api_name = request.form.get('api', config_manager.get('default_api'))
                model = request.form.get('model', config_manager.get('default_model'))
                prompt = request.form.get('prompt', '¿Qué hay en esta imagen?')
                
                # Validar API soporta imágenes
                if not self._api_supports_vision(api_name):
                    return jsonify({
                        'error': f'La API {api_name} no soporta análisis de imágenes'
                    }), 400
                
                # Guardar archivo temporalmente
                filename = secure_filename(file.filename)
                if not is_supported_image(filename):
                    return jsonify({
                        'error': 'Formato de imagen no soportado. Use: jpg, jpeg, png, webp'
                    }), 400
                
                filepath = os.path.join(self.upload_folder, filename)
                file.save(filepath)
                
                try:
                    # Validar tamaño
                    if not validate_file_size(filepath, 10 if self.is_mobile else 20):
                        return jsonify({
                            'error': f'Archivo demasiado grande. Máximo: {"10MB" if self.is_mobile else "20MB"}'
                        }), 400
                    
                    # Obtener API key y crear cliente
                    api_key = self.api_manager.get_api_key(api_name)
                    if not api_key:
                        return jsonify({'error': f'API key no configurada para {api_name}'}), 400
                    
                    client = UniversalAPIClient(api_key, self._get_api_base_url(api_name), api_name)
                    
                    # Crear mensaje con imagen
                    image_url = create_image_data_url(filepath)
                    messages = [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }]
                    
                    # Enviar a API
                    response = client.chat_completions(messages, model)
                    content = client.extract_response_content(response)
                    usage = client.get_usage_info(response)
                    
                    # Guardar en historial
                    conversation = {
                        "type": "mobile_image",
                        "api": api_name,
                        "model": model,
                        "file": filename,
                        "prompt": prompt,
                        "response": content,
                        "usage": usage,
                        "timestamp": datetime.now().isoformat()
                    }
                    save_conversation_history(conversation)
                    
                    return jsonify({
                        'response': content,
                        'model_used': model,
                        'api_used': api_name,
                        'usage': usage,
                        'filename': filename
                    })
                    
                finally:
                    # Limpiar archivo temporal
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        
            except Exception as e:
                return jsonify({'error': f'Error procesando imagen: {str(e)}'}), 500
        
        @self.app.route('/api/config', methods=['GET', 'POST'])
        def api_config():
            """Endpoint para gestión de configuración"""
            if request.method == 'GET':
                # Obtener configuración actual
                return jsonify({
                    'config': self._get_client_config(),
                    'api_providers': self._get_api_providers_info(),
                    'schemas': self._get_config_schemas()
                })
            else:
                # Actualizar configuración
                try:
                    data = request.get_json()
                    config_updates = data.get('config', {})
                    
                    success = True
                    errors = []
                    
                    for key, value in config_updates.items():
                        if not config_manager.set(key, value):
                            success = False
                            errors.append(f'Error actualizando {key}')
                    
                    if success:
                        return jsonify({
                            'success': True,
                            'message': 'Configuración actualizada correctamente'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'errors': errors
                        }), 400
                        
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': str(e)
                    }), 500
        
        @self.app.route('/api/api-keys', methods=['GET', 'POST', 'DELETE'])
        def api_keys():
            """Endpoint para gestión de API keys"""
            if request.method == 'GET':
                # Listar proveedores configurados
                providers = self.api_manager.list_providers()
                return jsonify({'providers': providers})
                
            elif request.method == 'POST':
                # Configurar nueva API key
                try:
                    data = request.get_json()
                    provider = data.get('provider')
                    api_key = data.get('api_key')
                    
                    if not provider or not api_key:
                        return jsonify({'error': 'Provider y API key requeridos'}), 400
                    
                    success = self.api_manager.set_api_key(provider, api_key)
                    if success:
                        return jsonify({
                            'success': True,
                            'message': f'API key configurada para {provider}'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Error configurando API key'
                        }), 400
                        
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                    
            elif request.method == 'DELETE':
                # Eliminar API key
                try:
                    provider = request.args.get('provider')
                    if not provider:
                        return jsonify({'error': 'Provider requerido'}), 400
                    
                    success = self.api_manager.remove_api_key(provider)
                    if success:
                        return jsonify({
                            'success': True,
                            'message': f'API key eliminada para {provider}'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Error eliminando API key'
                        }), 400
                        
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/validate-keys', methods=['POST'])
        def validate_keys():
            """Endpoint para validar API keys"""
            try:
                data = request.get_json()
                provider = data.get('provider')
                
                if provider:
                    # Validar proveedor específico
                    result = asyncio.run(self.api_manager.validate_api_key(provider, force_refresh=True))
                    return jsonify({'validation': {provider: result}})
                else:
                    # Validar todas las keys
                    results = asyncio.run(self.api_manager.validate_all_keys())
                    return jsonify({'validation': results})
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/history')
        def api_history():
            """Endpoint para obtener historial"""
            try:
                limit = request.args.get('limit', 50, type=int)
                history = load_conversation_history()
                recent = history[-limit:] if history else []
                
                return jsonify({
                    'history': recent,
                    'total': len(history)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats')
        def api_stats():
            """Endpoint para estadísticas de la aplicación"""
            try:
                # Obtener límites de archivos móviles
                file_limits = get_mobile_file_limits()
                
                return jsonify({
                    'app': {
                        'version': '1.0.0',
                        'is_mobile': self.is_mobile,
                        'platform': 'Termux' if self.is_mobile else 'Desktop'
                    },
                    'api_keys': self.api_manager.get_statistics(),
                    'config': config_manager.get_stats(),
                    'pwa': self.pwa_manager.get_cache_stats(),
                    'apis': get_api_statistics(),
                    'file_limits': file_limits,
                    'supported_features': {
                        'vision_apis': get_vision_supported_apis(),
                        'pdf_apis': get_pdf_supported_apis(),
                        'total_models': sum(len(get_available_models(api)) for api in AVAILABLE_APIS.keys())
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/console/stream')
        def console_stream():
            """Endpoint para streaming de logs de la consola."""
            def generate():
                # Bucle para mantener la conexión y enviar datos
                while True:
                    try:
                        # Esperar un mensaje de la cola
                        message = log_queue.get(timeout=20)
                        if message is None:  # Señal para cerrar la conexión
                            break
                        # Formatear como Server-Sent Event
                        yield f"data: {json.dumps(message)}\n\n"
                    except queue.Empty:
                        # Enviar un comentario para mantener la conexión viva
                        yield ": keep-alive\n\n"

            # Devolver una respuesta de streaming
            return Response(stream_with_context(generate()), mimetype='text/event-stream')

        @self.app.route('/api/interactive', methods=['POST'])
        def api_interactive():
            """Endpoint para shell interactivo y análisis de directorios."""
            data = request.json
            if not data or 'input' not in data:
                return jsonify({"error": "Invalid input"}), 400

            user_input = data['input'].strip()

            # Router de comandos
            if user_input.startswith('@analizar'):
                parts = user_input.split(' ', 1)
                if len(parts) < 2:
                    return jsonify({"status": "error", "output": "Uso: @analizar <directorio>"}), 400

                target_dir = parts[1]
                try:
                    analysis_path = self.interactive_shell.current_path / target_dir
                    analyzer = DirectoryAnalyzer(str(analysis_path))
                    analysis_result = analyzer.analyze()

                    output = ""
                    if analysis_result.get("documentation_summary"):
                        output += "--- Documentación Detectada ---\n"
                        output += analysis_result["documentation_summary"]
                    if analysis_result.get("content_samples"):
                        output += "\n--- Fragmentos de Archivos ---\n"
                        output += analysis_result["content_samples"]

                    if not output:
                        output = "Análisis completado. No se encontró documentación prioritaria ni archivos para muestrear."

                    return jsonify({"status": "ok", "output": output.strip()})
                except Exception as e:
                    return jsonify({"status": "error", "output": str(e)})
            else:
                result = self.interactive_shell.execute(user_input)

                if result["status"] == "passthrough":
                    # En la app móvil, passthrough significa que es un chat normal.
                    # Podríamos redirigirlo al endpoint de chat, pero por ahora lo marcamos.
                    result["output"] = f"Comando no reconocido o chat: {result['output']}"
                    result["status"] = "ok_passthrough"

                return jsonify(result)
    
    def _setup_error_handlers(self):
        """Configura manejadores de errores"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Endpoint no encontrado'}), 404
            return render_template('404.html'), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Error interno del servidor'}), 500
            return render_template('500.html'), 500
        
        @self.app.errorhandler(413)
        def too_large(error):
            return jsonify({'error': 'Archivo demasiado grande'}), 413
    
    def _get_client_config(self) -> Dict:
        """Obtiene configuración para el cliente"""
        return {
            'theme': config_manager.get('theme'),
            'language': config_manager.get('language'),
            'default_api': config_manager.get('default_api'),
            'default_model': config_manager.get('default_model'),
            'show_token_usage': config_manager.get('show_token_usage'),
            'compact_mode': config_manager.get('compact_mode'),
            'animations_enabled': config_manager.get('animations_enabled'),
            'offline_mode': config_manager.get('offline_mode'),
            'notifications_enabled': config_manager.get('notifications_enabled'),
            'is_mobile': self.is_mobile
        }
    
    def _get_api_providers_info(self) -> List[Dict]:
        """Obtiene información de proveedores de API usando configuración extendida"""
        providers = []
        configured_providers = self.api_manager.list_providers()
        configured_names = {p['provider'] for p in configured_providers}
        
        for provider_id, config in AVAILABLE_APIS.items():
            provider_info = {
                'id': provider_id,
                'name': config['name'],
                'supports_vision': config.get('supports_vision', False),
                'supports_pdf': config.get('supports_pdf', False),
                'configured': provider_id in configured_names,
                'status': 'unknown',
                'models_count': len(get_available_models(provider_id))
            }
            
            # Agregar información de estado si está configurado
            if provider_id in configured_names:
                configured_info = next(p for p in configured_providers if p['provider'] == provider_id)
                provider_info.update({
                    'status': configured_info['validation_status'],
                    'last_validated': configured_info['last_validated'],
                    'usage_count': configured_info['usage_count']
                })
            
            providers.append(provider_info)
        
        return providers
    
    def _get_config_schemas(self) -> List[Dict]:
        """Obtiene esquemas de configuración para el cliente"""
        schemas = []
        for schema in config_manager.list_schemas():
            schemas.append({
                'key': schema.key,
                'type': schema.type.__name__,
                'default': schema.default,
                'required': schema.required,
                'description': schema.description,
                'scope': schema.scope.value
            })
        return schemas
    
    def _get_api_base_url(self, api_name: str) -> str:
        """Obtiene URL base para una API usando configuración extendida"""
        config = get_api_config(api_name)
        return config.get('base_url', 'https://api.blackbox.ai')
    
    def _api_supports_vision(self, api_name: str) -> bool:
        """Verifica si una API soporta análisis de imágenes usando configuración extendida"""
        return api_name in get_vision_supported_apis()
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecuta la aplicación"""
        print(f"🌐 Iniciando Chispart Mobile en http://{host}:{port}")
        print(f"📱 Modo: {'Móvil (Termux)' if self.is_mobile else 'Desktop'}")
        print(f"🔧 Debug: {'Activado' if debug else 'Desactivado'}")
        
        if self.is_mobile:
            print(f"📲 Acceso desde otros dispositivos: http://[tu-ip]:{port}")
            print("💡 Mantén la pantalla encendida para evitar que se cierre")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)

# Crear instancia de la aplicación
app_instance = ChispartMobileApp()
app = app_instance.app  # Para compatibilidad con servidores WSGI

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Chispart Mobile - Universal LLM Terminal')
    parser.add_argument('--host', default='0.0.0.0', help='Host para el servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto para el servidor')
    parser.add_argument('--debug', action='store_true', help='Activar modo debug')
    
    args = parser.parse_args()
    
    # Configurar debug basado en entorno
    debug_mode = args.debug or os.getenv('FLASK_ENV') == 'development'
    
    # Ejecutar aplicación
    app_instance.run(host=args.host, port=args.port, debug=debug_mode)
