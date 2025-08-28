"""
Servidor Flask para sesiones de Split Chat
Cada sesión split ejecuta su propio servidor Flask
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys
import json
from datetime import datetime
from typing import Optional

# Añadir el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import UniversalAPIClient, APIError
from config_extended import get_api_config, get_available_models, get_default_model
from core.dev_profiles import profile_manager

def create_split_server(session_id: str, profile: str = "", model: str = ""):
    """Crea una aplicación Flask para una sesión split específica"""
    
    app = Flask(__name__)
    app.config['SESSION_ID'] = session_id
    app.config['PROFILE'] = profile
    app.config['MODEL'] = model or get_default_model()
    
    # Configurar perfil si se especifica
    if profile:
        profile_manager.set_current_profile(profile)
    
    @app.route('/')
    def home():
        """Página principal del split chat"""
        return render_template_string(SPLIT_CHAT_TEMPLATE, 
                                    session_id=session_id,
                                    profile=profile,
                                    model=app.config['MODEL'])
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Endpoint de chat para esta sesión"""
        try:
            data = request.json
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({'error': 'Mensaje vacío'}), 400
            
            # Obtener configuración de API
            config = get_api_config('chispart')
            if not config["api_key"]:
                return jsonify({'error': 'API key no configurada'}), 400
            
            # Crear cliente API
            client = UniversalAPIClient(config["api_key"], config["base_url"], config["name"])
            
            # Preparar mensajes
            messages = []
            
            # Añadir system prompt del perfil si existe
            if profile:
                system_prompt = profile_manager.get_system_prompt(profile)
                if system_prompt:
                    messages.append({
                        "role": "system",
                        "content": system_prompt
                    })
            
            # Añadir mensaje del usuario
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Obtener modelo
            available_models = get_available_models('chispart')
            model_name = available_models.get(app.config['MODEL'], available_models['gpt-4'])
            
            # Enviar a API
            response = client.chat_completions(messages, model_name)
            content = client.extract_response_content(response)
            usage = client.get_usage_info(response)
            
            # Guardar en historial de la sesión
            _save_message_to_session(session_id, message, content, usage)
            
            return jsonify({
                'response': content,
                'model_used': app.config['MODEL'],
                'usage': usage,
                'session_id': session_id,
                'profile': profile
            })
            
        except APIError as e:
            return jsonify({
                'error': f"Error de API: {e.message}",
                'status_code': e.status_code
            }), 500
        except Exception as e:
            return jsonify({'error': f"Error inesperado: {str(e)}"}), 500
    
    @app.route('/api/status')
    def status():
        """Estado de la sesión split"""
        return jsonify({
            'session_id': session_id,
            'profile': profile,
            'model': app.config['MODEL'],
            'status': 'active',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/history')
    def history():
        """Historial de la sesión"""
        messages = _load_session_messages(session_id)
        return jsonify({
            'session_id': session_id,
            'messages': messages,
            'count': len(messages)
        })
    
    return app

def _save_message_to_session(session_id: str, user_message: str, 
                           assistant_response: str, usage: dict):
    """Guarda un mensaje en el historial de la sesión"""
    try:
        session_file = f"split_session_{session_id}.json"
        
        # Cargar historial existente
        messages = []
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                data = json.load(f)
                messages = data.get('messages', [])
        
        # Añadir nuevos mensajes
        timestamp = datetime.now().isoformat()
        messages.extend([
            {
                "role": "user",
                "content": user_message,
                "timestamp": timestamp
            },
            {
                "role": "assistant", 
                "content": assistant_response,
                "timestamp": timestamp,
                "usage": usage
            }
        ])
        
        # Guardar
        with open(session_file, 'w') as f:
            json.dump({
                'session_id': session_id,
                'messages': messages,
                'last_updated': timestamp
            }, f, indent=2)
            
    except Exception as e:
        print(f"Error guardando mensaje: {e}")

def _load_session_messages(session_id: str) -> list:
    """Carga los mensajes de una sesión"""
    try:
        session_file = f"split_session_{session_id}.json"
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                data = json.load(f)
                return data.get('messages', [])
    except Exception as e:
        print(f"Error cargando mensajes: {e}")
    
    return []

# Template HTML para la interfaz de split chat
SPLIT_CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chispart Split Chat - {{ session_id }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #ffffff;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(0, 255, 136, 0.1);
            border-bottom: 2px solid #00ff88;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .session-info {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .badge {
            background: #00ff88;
            color: #000;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .message {
            max-width: 80%;
            padding: 1rem;
            border-radius: 1rem;
            word-wrap: break-word;
        }
        
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000;
        }
        
        .message.assistant {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .input-container {
            padding: 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .input-form {
            display: flex;
            gap: 0.5rem;
        }
        
        .message-input {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #00ff88;
            border-radius: 0.5rem;
            background: rgba(0, 0, 0, 0.5);
            color: #ffffff;
            font-size: 1rem;
        }
        
        .message-input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .send-button {
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000;
            border: none;
            border-radius: 0.5rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 1rem;
            color: #00ff88;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 255, 136, 0.3);
            border-radius: 50%;
            border-top-color: #00ff88;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="session-info">
            <h2>🚀 Chispart Split Chat</h2>
            <span class="badge">{{ session_id }}</span>
            {% if profile %}
            <span class="badge">{{ profile }}</span>
            {% endif %}
            <span class="badge">{{ model }}</span>
        </div>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message assistant">
                <strong>🤖 Asistente:</strong><br>
                ¡Hola! Soy tu asistente de IA en esta sesión split.
                {% if profile %}
                <br><br>📋 <strong>Perfil activo:</strong> {{ profile }}
                {% endif %}
                <br><br>💬 Escribe tu mensaje para comenzar la conversación.
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            Procesando mensaje...
        </div>
        
        <div class="input-container">
            <form class="input-form" id="chatForm">
                <input 
                    type="text" 
                    class="message-input" 
                    id="messageInput" 
                    placeholder="Escribe tu mensaje aquí..."
                    required
                >
                <button type="submit" class="send-button" id="sendButton">
                    Enviar
                </button>
            </form>
        </div>
    </div>

    <script>
        const messagesContainer = document.getElementById('messages');
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const loading = document.getElementById('loading');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Añadir mensaje del usuario
            addMessage(message, 'user');
            
            // Limpiar input y deshabilitar
            messageInput.value = '';
            sendButton.disabled = true;
            loading.style.display = 'block';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    addMessage(data.response, 'assistant');
                } else {
                    addMessage(`Error: ${data.error}`, 'assistant');
                }
            } catch (error) {
                addMessage(`Error de conexión: ${error.message}`, 'assistant');
            } finally {
                sendButton.disabled = false;
                loading.style.display = 'none';
                messageInput.focus();
            }
        });

        function addMessage(content, role) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            if (role === 'user') {
                messageDiv.innerHTML = `<strong>👤 Tú:</strong><br>${content}`;
            } else {
                messageDiv.innerHTML = `<strong>🤖 Asistente:</strong><br>${content}`;
            }
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Enfocar input al cargar
        messageInput.focus();
    </script>
</body>
</html>
'''
