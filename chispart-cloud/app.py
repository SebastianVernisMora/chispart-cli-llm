from flask import Flask, jsonify, request
from flask_socketio import SocketIO, join_room
from core.models import Run, Workflow # Workflow might be used later
from tasks import execute_run
import os

app = Flask(__name__)
# Make sure to configure the message queue for SocketIO
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, message_queue=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))

# Using a simple in-memory model for now, as in the original code
workflow_model = Workflow()
run_model = Run()

@app.route('/')
def index():
    return "Chispart Cloud MCP Runtime"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.json
    if not data or 'command' not in data:
        return jsonify({"error": "Invalid input, 'command' field is required"}), 400

    command_string = data['command']

    # Create a new run record
    # In a real app, this might be associated with a workflow
    run_data = {
        'workflow_id': data.get('workflow_id', None),
        'status': 'queued',
        'command': command_string
    }
    new_run = run_model.create(run_data)

    # Trigger the background task
    execute_run.delay(new_run['id'], command_string)

    # Return the run ID so the client can listen for updates
    return jsonify(new_run), 202 # 202 Accepted

@app.route('/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    run = run_model.get_by_id(run_id)
    if run:
        return jsonify(run)
    return jsonify({"error": "Run not found"}), 404

@app.route('/runs', methods=['GET'])
def list_runs():
    runs = run_model.get_all()
    return jsonify(runs)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('subscribe_to_run')
def handle_subscribe_to_run(data):
    run_id = data.get('run_id')
    if run_id:
        room = f'run_{run_id}'
        join_room(room)
        print(f'Client {request.sid} subscribed to room {room}')
        # Optionally send back a confirmation
        socketio.emit('subscribed', {'run_id': run_id}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
