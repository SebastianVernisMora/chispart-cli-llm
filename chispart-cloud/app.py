from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.shell import InteractiveShell
from core.analyzer import DirectoryAnalyzer
from core.models import Workflow, Run
from tasks import execute_run
import os

app = Flask(__name__)
socketio = SocketIO(app, message_queue='redis://localhost:6379/0')
workflow_model = Workflow()
run_model = Run()

# Instancia global del shell para mantener el estado de la sesión.
# Nota: Esto no es seguro para hilos en un entorno de producción real.
interactive_shell = InteractiveShell()

@app.route('/')
def index():
    return "Chispart Cloud Tools - Interactive API"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/workflows', methods=['GET', 'POST'])
def workflows():
    if request.method == 'POST':
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Invalid input"}), 400
        workflow = workflow_model.create(data)
        return jsonify(workflow), 201
    else:
        workflows = workflow_model.get_all()
        return jsonify(workflows)

@app.route('/workflows/<int:workflow_id>', methods=['GET'])
def workflow(workflow_id):
    workflow = workflow_model.get_by_id(workflow_id)
    if workflow:
        return jsonify(workflow)
    return jsonify({"error": "Workflow not found"}), 404

@app.route('/runs', methods=['GET', 'POST'])
def runs():
    if request.method == 'POST':
        data = request.json
        if not data or 'workflow_id' not in data:
            return jsonify({"error": "Invalid input"}), 400

        data['status'] = 'queued'
        run = run_model.create(data)
        execute_run.delay(run['id'], run['workflow_id'])
        return jsonify(run), 201
    else:
        runs = run_model.get_all()
        return jsonify(runs)

@app.route('/runs/<int:run_id>', methods=['GET'])
def run(run_id):
    run = run_model.get_by_id(run_id)
    if run:
        return jsonify(run)
    return jsonify({"error": "Run not found"}), 404

@app.route('/api/interactive', methods=['POST'])
def interactive_endpoint():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "Invalid input"}), 400

    user_input = data['input'].strip()

    # Router de comandos
    if user_input.startswith('@analizar'):
        # Comando de análisis de directorio
        parts = user_input.split(' ', 1)
        if len(parts) < 2:
            return jsonify({"status": "error", "output": "Uso: @analizar <directorio>"}), 400

        target_dir = parts[1]
        try:
            # Usar el directorio de trabajo actual del shell como base
            analysis_path = interactive_shell.current_path / target_dir
            analyzer = DirectoryAnalyzer(str(analysis_path))
            analysis_result = analyzer.analyze()

            # Formatear la salida para el JSON
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
        # Pasar el comando al shell interactivo
        result = interactive_shell.execute(user_input)

        if result["status"] == "passthrough":
            # El shell no manejó el comando, tratarlo como chat
            # En un futuro, esto se pasaría a un LLM
            result["output"] = f"Comando no reconocido o chat: {result['output']}"
            result["status"] = "ok"

        return jsonify(result)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe')
def handle_subscribe(data):
    room = data.get('room')
    join_room(room)
    emit('status', {'msg': f'Subscribed to room {room}'}, room=request.sid)

if __name__ == '__main__':
    # Usar el puerto 8080 para evitar conflictos comunes y desactivar el reloader para mantener el estado
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False)
