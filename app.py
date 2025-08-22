from flask import Flask, request, jsonify, render_template_string, Response
import os
import sys
import json
import time
import uuid
from datetime import datetime
from functools import wraps

# Importar nuestros módulos CLI
from api_client import UniversalAPIClient, APIError
from config import (
    get_api_config, get_available_models, get_default_model, 
    AVAILABLE_APIS, DEFAULT_API, VISION_SUPPORTED_APIS, PDF_SUPPORTED_APIS
)
from utils import (
    is_supported_image, is_supported_pdf, create_image_data_url,
    extract_text_from_pdf, save_conversation_history, load_conversation_history,
    format_file_size, validate_file_size
)
from logger_config import get_logger, LoggerMixin

app = Flask(__name__)

# Configurar logging para Flask
app.logger = get_logger('flask_app')

class WebAppLogger(LoggerMixin):
    """Clase para manejar logging específico de la aplicación web"""
    pass

web_logger = WebAppLogger()

def log_request(f):
    """Decorador para logging automático de requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log del inicio de la request
        web_logger.logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
        )
        
        try:
            # Ejecutar la función
            result = f(*args, **kwargs)
            
            # Calcular tiempo de ejecución
            execution_time = (time.time() - start_time) * 1000
            
            # Log de éxito
            status_code = result[1] if isinstance(result, tuple) else 200
            web_logger.logger.info(
                f"Request completed successfully: {request.method} {request.path}",
                extra={
                    'request_id': request_id,
                    'execution_time': execution_time,
                    'status_code': status_code
                }
            )
            
            return result
            
        except Exception as e:
            # Calcular tiempo de ejecución
            execution_time = (time.time() - start_time) * 1000
            
            # Log de error
            web_logger.log_error(
                e,
                context={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'execution_time': execution_time
                }
            )
            
            raise
    
    return decorated_function

def validate_api_key(api_name):
    """Valida que la clave API esté configurada para la API especificada"""
    web_logger.logger.debug(f"Validating API key for: {api_name}")
    
    config = get_api_config(api_name)
    if not config["api_key"] or config["api_key"] == "your_api_key_here":
        web_logger.logger.warning(
            f"API key not configured for {api_name}",
            extra={'api_name': api_name}
        )
        return None, f"Clave API no configurada para {config['name']}"
    
    web_logger.logger.debug(f"API key validated successfully for: {api_name}")
    return config, None

def create_text_message(content: str) -> dict:
    """Crea un mensaje de texto"""
    return {
        "role": "user",
        "content": content
    }

@app.route('/')
@log_request
def home():
    """Página principal con la interfaz de chat"""
    web_logger.log_user_action("page_access", session_id=request.headers.get('X-Session-ID'))
    return app.send_static_file('chat_interface.html')

@app.route('/api/models/<api_name>')
@log_request
def get_models(api_name):
    """Obtiene los modelos disponibles para una API específica"""
    web_logger.logger.info(f"Fetching models for API: {api_name}")
    
    try:
        if api_name not in AVAILABLE_APIS:
            web_logger.logger.warning(f"Unsupported API requested: {api_name}")
            return jsonify({'error': f'API {api_name} no soportada'}), 400
        
        config, error = validate_api_key(api_name)
        if error:
            return jsonify({'error': error}), 400
        
        available_models = get_available_models(api_name)
        default_model = get_default_model(api_name)
        
        web_logger.logger.info(
            f"Models fetched successfully for {api_name}",
            extra={
                'api_name': api_name,
                'model_count': len(available_models),
                'default_model': default_model
            }
        )
        
        return jsonify({
            'api_name': config['name'],
            'models': available_models,
            'default_model': default_model
        })
    except Exception as e:
        web_logger.log_error(e, context={'api_name': api_name})
        return jsonify({'error': str(e)}), 500

@app.route('/api/apis')
@log_request
def get_apis():
    """Obtiene la lista de APIs disponibles"""
    web_logger.logger.info("Fetching available APIs")
    
    try:
        apis_info = []
        for api_key, api_info in AVAILABLE_APIS.items():
            config, error = validate_api_key(api_key)
            status = "configured" if not error else "not_configured"
            
            apis_info.append({
                'key': api_key,
                'name': api_info['name'],
                'status': status,
                'supports_vision': api_key in VISION_SUPPORTED_APIS,
                'supports_pdf': api_key in PDF_SUPPORTED_APIS
            })
        
        configured_count = sum(1 for api in apis_info if api['status'] == 'configured')
        web_logger.logger.info(
            f"APIs fetched successfully: {configured_count}/{len(apis_info)} configured"
        )
        
        return jsonify({
            'apis': apis_info,
            'default_api': DEFAULT_API
        })
    except Exception as e:
        web_logger.log_error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
@log_request
def chat():
    """Endpoint principal para el chat, soporta streaming."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    data = request.json
    message = data.get('message', '').strip()
    api_name = data.get('api', DEFAULT_API)
    model = data.get('model')
    stream = data.get('stream', False)

    try:
        web_logger.log_user_action("chat_message_sent", request_id=request_id, api_name=api_name, model_name=model, message_length=len(message), stream=stream)
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        config, error = validate_api_key(api_name)
        if error:
            return jsonify({'error': error}), 400

        available_models = get_available_models(api_name)
        if not model:
            model = get_default_model(api_name)
        elif model not in available_models:
            return jsonify({'error': f"Modelo '{model}' no disponible para {config['name']}"}), 400

        client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
        messages = [create_text_message(message)]
        model_name = available_models[model]

        if not stream:
            # Lógica original para no-streaming
            response = client.chat_completions(messages, model_name, stream=False)
            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)

            conversation = {"type": "web_chat", "api": api_name, "model": model, "message": message, "response": content, "usage": usage, "timestamp": datetime.now().isoformat(), "request_id": request_id}
            save_conversation_history(conversation)

            return jsonify({'response': content, 'model_used': model, 'api_used': config['name'], 'usage': usage})

        else:
            # Nueva lógica para streaming
            def stream_generator():
                try:
                    full_response = []
                    for chunk in client.chat_completions(messages, model_name, stream=True):
                        content_chunk = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content_chunk:
                            full_response.append(content_chunk)
                            data_to_send = {"type": "content", "chunk": content_chunk}
                            yield f"data: {json.dumps(data_to_send)}\n\n"

                    # Cuando termina, guardar la conversación completa
                    final_text = "".join(full_response)
                    conversation = {"type": "web_chat_stream", "api": api_name, "model": model, "message": message, "response": final_text, "usage": None, "timestamp": datetime.now().isoformat(), "request_id": request_id}
                    save_conversation_history(conversation)

                    # Enviar un evento de finalización
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"

                except APIError as e:
                    error_data = {"type": "error", "message": f"Error de {e.api_name}: {e.message}"}
                    yield f"data: {json.dumps(error_data)}\n\n"
                except Exception as e:
                    error_data = {"type": "error", "message": f"Error inesperado durante el streaming: {str(e)}"}
                    yield f"data: {json.dumps(error_data)}\n\n"

            return Response(stream_generator(), mimetype='text/event-stream')

    except APIError as e:
        web_logger.log_error(
            e,
            context={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': model,
                'error_type': 'api_error'
            },
            error_code=f"API_{e.status_code}"
        )
        return jsonify({
            'error': f"Error de {e.api_name}: {e.message}",
            'status_code': e.status_code
        }), 500
    except Exception as e:
        web_logger.log_error(
            e,
            context={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': model,
                'error_type': 'unexpected_error'
            }
        )
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500

@app.route('/api/history')
@log_request
def get_history():
    """Obtiene el historial de conversaciones en formato raw."""
    try:
        limit = request.args.get('limit', 50, type=int) # Aumentar límite para tener más contexto
        web_logger.logger.info(f"Fetching raw history with limit: {limit}")
        
        history = load_conversation_history()
        
        # Devolver las últimas N conversaciones, en orden cronológico (más antiguas primero)
        recent_conversations = history[-limit:]
        
        web_logger.logger.info(
            f"Raw history fetched successfully: {len(recent_conversations)} conversations"
        )
        
        return jsonify({
            'history': recent_conversations,
            'total_conversations': len(history)
        })
    except Exception as e:
        web_logger.log_error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/image', methods=['POST'])
@log_request
def analyze_image():
    """Endpoint para análisis de imágenes"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Verificar si se subió un archivo
        if 'image' not in request.files:
            web_logger.logger.warning("No image file provided", extra={'request_id': request_id})
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        file = request.files['image']
        if file.filename == '':
            web_logger.logger.warning("Empty filename provided", extra={'request_id': request_id})
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        # Obtener parámetros
        api_name = request.form.get('api', DEFAULT_API)
        model = request.form.get('model')
        prompt = request.form.get('prompt', '¿Qué hay en esta imagen?')
        
        web_logger.log_user_action(
            "image_analysis_requested",
            request_id=request_id,
            api_name=api_name,
            model_name=model,
            filename=file.filename,
            file_size=len(file.read())
        )
        file.seek(0)  # Reset file pointer
        
        # Verificar si la API soporta imágenes
        if api_name not in VISION_SUPPORTED_APIS:
            web_logger.logger.warning(
                f"API {api_name} does not support vision",
                extra={'request_id': request_id, 'api_name': api_name}
            )
            return jsonify({
                'error': f'La API {AVAILABLE_APIS[api_name]["name"]} no soporta análisis de imágenes',
                'supported_apis': [AVAILABLE_APIS[api]['name'] for api in VISION_SUPPORTED_APIS]
            }), 400
        
        # Validar API
        config, error = validate_api_key(api_name)
        if error:
            return jsonify({'error': error}), 400
        
        # Guardar archivo temporalmente
        filename = file.filename
        if not is_supported_image(filename):
            web_logger.logger.warning(
                f"Unsupported image format: {filename}",
                extra={'request_id': request_id, 'filename': filename}
            )
            return jsonify({'error': 'Formato de imagen no soportado. Use: jpg, jpeg, png, webp'}), 400
        
        temp_path = f"/tmp/{request_id}_{filename}"
        file.save(temp_path)
        
        # Validar tamaño
        file_size = os.path.getsize(temp_path)
        if not validate_file_size(temp_path, 20):
            os.remove(temp_path)
            formatted_size = format_file_size(file_size)
            web_logger.logger.warning(
                f"File too large: {formatted_size}",
                extra={'request_id': request_id, 'file_size': file_size}
            )
            return jsonify({'error': f'Archivo demasiado grande ({formatted_size}). Máximo: 20MB'}), 400
        
        # Obtener modelos y validar
        available_models = get_available_models(api_name)
        if not model:
            model = "gpt-4-vision" if "gpt-4-vision" in available_models else get_default_model(api_name)
        elif model not in available_models:
            os.remove(temp_path)
            web_logger.logger.warning(
                f"Invalid model for image analysis: {model}",
                extra={'request_id': request_id, 'api_name': api_name, 'model_name': model}
            )
            return jsonify({
                'error': f"Modelo '{model}' no disponible para {config['name']}",
                'available_models': list(available_models.keys())
            }), 400
        
        # Crear mensaje con imagen
        try:
            web_logger.logger.info(
                f"Processing image with {api_name}/{model}",
                extra={'request_id': request_id, 'api_name': api_name, 'model_name': model}
            )
            
            image_url = create_image_data_url(temp_path)
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }]
            
            # Enviar a la API
            client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
            model_name = available_models[model]
            
            api_start_time = time.time()
            response = client.chat_completions(messages, model_name)
            api_execution_time = (time.time() - api_start_time) * 1000
            
            # Extraer respuesta
            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)
            
            # Log de la llamada a la API
            web_logger.log_api_call(
                api_name=api_name,
                model_name=model,
                execution_time=api_execution_time,
                tokens_used=usage.get('total_tokens') if usage else None,
                request_id=request_id
            )
            
            # Guardar en historial
            conversation = {
                "type": "web_image",
                "api": api_name,
                "model": model,
                "file": filename,
                "prompt": prompt,
                "response": content,
                "usage": usage,
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            }
            save_conversation_history(conversation)
            
            total_execution_time = (time.time() - start_time) * 1000
            web_logger.logger.info(
                f"Image analysis completed successfully",
                extra={
                    'request_id': request_id,
                    'api_name': api_name,
                    'model_name': model,
                    'execution_time': total_execution_time,
                    'tokens_used': usage.get('total_tokens') if usage else None,
                    'response_length': len(content)
                }
            )
            
            return jsonify({
                'response': content,
                'model_used': model,
                'api_used': config['name'],
                'usage': usage,
                'filename': filename
            })
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
                web_logger.logger.debug(f"Temporary file cleaned up: {temp_path}")
        
    except APIError as e:
        web_logger.log_error(
            e,
            context={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': model,
                'error_type': 'api_error'
            },
            error_code=f"API_{e.status_code}"
        )
        return jsonify({
            'error': f"Error de {e.api_name}: {e.message}",
            'status_code': e.status_code
        }), 500
    except Exception as e:
        web_logger.log_error(
            e,
            context={
                'request_id': request_id,
                'api_name': api_name,
                'model_name': model,
                'error_type': 'unexpected_error'
            }
        )
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500


@app.route('/api/pdf', methods=['POST'])
@log_request
def analyze_pdf():
    """Endpoint para análisis de PDFs"""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        if 'pdf' not in request.files:
            web_logger.logger.warning("No PDF file provided", extra={'request_id': request_id})
            return jsonify({'error': 'No se proporcionó archivo PDF'}), 400

        file = request.files['pdf']
        if file.filename == '':
            web_logger.logger.warning("Empty filename for PDF provided", extra={'request_id': request_id})
            return jsonify({'error': 'No se seleccionó archivo'}), 400

        api_name = request.form.get('api', DEFAULT_API)
        model = request.form.get('model')
        prompt = request.form.get('prompt', 'Resume el contenido de este documento PDF.')

        web_logger.log_user_action("pdf_analysis_requested", request_id=request_id, api_name=api_name, model_name=model, filename=file.filename)

        if api_name not in PDF_SUPPORTED_APIS:
            web_logger.logger.warning(f"API {api_name} does not support PDF", extra={'request_id': request_id, 'api_name': api_name})
            return jsonify({'error': f'La API {AVAILABLE_APIS[api_name]["name"]} no soporta análisis de PDF'}), 400

        config, error = validate_api_key(api_name)
        if error:
            return jsonify({'error': error}), 400

        filename = file.filename
        if not is_supported_pdf(filename):
            web_logger.logger.warning(f"Unsupported PDF format: {filename}", extra={'request_id': request_id})
            return jsonify({'error': 'Formato de archivo no soportado. Use: .pdf'}), 400

        temp_path = f"/tmp/{request_id}_{filename}"
        file.save(temp_path)

        if not validate_file_size(temp_path, 20):
            os.remove(temp_path)
            formatted_size = format_file_size(os.path.getsize(temp_path))
            web_logger.logger.warning(f"PDF file too large: {formatted_size}", extra={'request_id': request_id})
            return jsonify({'error': f'Archivo demasiado grande ({formatted_size}). Máximo: 20MB'}), 400

        available_models = get_available_models(api_name)
        if not model:
            model = get_default_model(api_name)
        elif model not in available_models:
            os.remove(temp_path)
            web_logger.logger.warning(f"Invalid model for PDF analysis: {model}", extra={'request_id': request_id})
            return jsonify({'error': f"Modelo '{model}' no disponible para {config['name']}"}), 400

        try:
            web_logger.logger.info(f"Extracting text from PDF: {filename}", extra={'request_id': request_id})
            pdf_text = extract_text_from_pdf(temp_path)

            max_chars = 100000
            if len(pdf_text) > max_chars:
                pdf_text = pdf_text[:max_chars] + "\n\n[... CONTENIDO TRUNCADO ...]"

            full_prompt = f"Se ha extraído el siguiente texto de un documento PDF ('{filename}'):\n\n---\n{pdf_text}\n---\n\nPor favor, responde a la siguiente pregunta basada en el texto del documento:\n\n{prompt}"

            messages = [create_text_message(full_prompt)]
            client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
            model_name = available_models[model]

            api_start_time = time.time()
            response = client.chat_completions(messages, model_name)
            api_execution_time = (time.time() - api_start_time) * 1000

            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)

            web_logger.log_api_call(api_name=api_name, model_name=model, execution_time=api_execution_time, tokens_used=usage.get('total_tokens') if usage else None, request_id=request_id)

            conversation = {
                "type": "web_pdf", "api": api_name, "model": model, "file": filename,
                "prompt": prompt, "response": content, "usage": usage,
                "timestamp": datetime.now().isoformat(), "request_id": request_id
            }
            save_conversation_history(conversation)

            total_execution_time = (time.time() - start_time) * 1000
            web_logger.logger.info("PDF analysis completed successfully", extra={'request_id': request_id, 'execution_time': total_execution_time})

            return jsonify({'response': content, 'model_used': model, 'api_used': config['name'], 'usage': usage, 'filename': filename})

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                web_logger.logger.debug(f"Temporary PDF file cleaned up: {temp_path}", extra={'request_id': request_id})

    except APIError as e:
        web_logger.log_error(e, context={'request_id': request_id, 'api_name': api_name, 'model_name': model, 'error_type': 'api_error'}, error_code=f"API_{e.status_code}")
        return jsonify({'error': f"Error de {e.api_name}: {e.message}", 'status_code': e.status_code}), 500
    except Exception as e:
        web_logger.log_error(e, context={'request_id': request_id, 'api_name': api_name, 'model_name': model, 'error_type': 'unexpected_error'})
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    """Manejador de errores 404"""
    web_logger.logger.warning(
        f"404 Not Found: {request.path}",
        extra={
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr
        }
    )
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500"""
    web_logger.logger.error(
        f"500 Internal Server Error: {request.path}",
        extra={
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr
        }
    )
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    web_logger.logger.info("Starting Flask application")
    web_logger.logger.info(f"Available APIs: {list(AVAILABLE_APIS.keys())}")
    web_logger.logger.info(f"Default API: {DEFAULT_API}")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        web_logger.log_error(e, context={'component': 'flask_startup'})
        raise
