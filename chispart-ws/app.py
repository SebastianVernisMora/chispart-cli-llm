from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from core.shell import InteractiveShell
from core.analyzer import DirectoryAnalyzer
from auth import generate_token, validate_token
from logger_config import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Store a shell instance for each client
sessions = {}

@app.route('/')
def index():
    return "Chispart WS-RPC Server"

@app.route('/get-token/<user_id>')
def get_token(user_id):
    """
    Generates a JWT for a given user ID.
    In a real app, you'd have a proper login system.
    """
    token = generate_token(user_id)
    logger.info(f"Generated token for user_id: {user_id}")
    return jsonify({'token': token})

@socketio.on('connect')
def handle_connect():
    """
    Handles a new client connection, with authentication.
    """
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1] if auth_header else None

    if not token:
        logger.warning(f"Connection rejected for sid {request.sid}: No token provided.")
        return False  # Reject connection

    payload = validate_token(token)
    if not payload:
        logger.warning(f"Connection rejected for sid {request.sid}: Invalid token.")
        return False  # Reject connection

    user_id = payload['user_id']
    sid = request.sid
    logger.info(f"Client connected: {sid}, user_id: {user_id}")
    sessions[sid] = {"shell": InteractiveShell(), "user_id": user_id}
    emit('connection_response', {'status': 'ok', 'sid': sid})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles a client disconnection.
    """
    logger.info(f"Client disconnected: {request.sid}")
    if request.sid in sessions:
        del sessions[request.sid]

@socketio.on('shell_command')
def handle_shell_command(data):
    """
    Handles a shell command from a client.
    """
    if 'command' not in data:
        logger.error(f"Invalid shell command format from {request.sid}")
        emit('shell_response', {'status': 'error', 'output': 'Invalid command format'})
        return

    command = data['command']
    logger.info(f"Received shell command from {request.sid}: {command}")
    session = sessions.get(request.sid)
    if session:
        result = session["shell"].execute(command)
        emit('shell_response', result)
    else:
        logger.error(f"Shell not initialized for {request.sid}")
        emit('shell_response', {'status': 'error', 'output': 'Shell not initialized'})

@socketio.on('analyze_directory')
def handle_analyze_directory(data):
    """
    Handles a directory analysis request from a client.
    """
    if 'directory' not in data:
        logger.error(f"Invalid analysis request format from {request.sid}")
        emit('analysis_response', {'status': 'error', 'output': 'Invalid analysis request format'})
        return

    directory = data['directory']
    logger.info(f"Received analysis request from {request.sid} for directory: {directory}")
    session = sessions.get(request.sid)
    if session:
        try:
            analysis_path = session["shell"].current_path / directory
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

            emit('analysis_response', {"status": "ok", "output": output.strip()})
        except Exception as e:
            logger.error(f"Error during analysis for {request.sid}: {e}")
            emit('analysis_response', {"status": "error", "output": str(e)})
    else:
        logger.error(f"Shell not initialized for {request.sid}")
        emit('analysis_response', {'status': 'error', 'output': 'Shell not initialized'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, allow_unsafe_werkzeug=True)
