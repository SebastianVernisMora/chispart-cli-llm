from flask import Flask, jsonify, request
from flask_socketio import SocketIO, join_room
from core.models import Run, Workflow, Task
from tasks import execute_run, celery
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False') == 'True'

# Celery configuration
app.config.update(
    broker_url=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
    result_backend=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
)

if app.config['TESTING']:
    socketio = SocketIO(app)
    app.config.update(task_always_eager=True)
else:
    socketio = SocketIO(app, message_queue=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))

celery.conf.update(app.config)
# Attach the socketio instance to the celery app
celery.socketio = socketio


workflow_model = Workflow()
run_model = Run()
task_model = Task()

@app.route('/')
def index():
    return "Chispart Cloud MCP Runtime"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/execute', methods=['POST'])
def execute():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    command_string = data.get('command')
    workflow_yaml = data.get('workflow')

    if not command_string and not workflow_yaml:
        return jsonify({"error": "Either 'command' or 'workflow' field is required"}), 400

    run_data = {
        'workflow_id': data.get('workflow_id'),
        'status': 'queued',
        'command': command_string,
        'workflow_yaml': workflow_yaml
    }
    new_run = run_model.create(run_data)

    execute_run.delay(new_run['id'], command_string, workflow_yaml)

    return jsonify(new_run), 202

@app.route('/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    run = run_model.get_by_id(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404

    run['tasks'] = task_model.find_by_run_id(run_id)
    return jsonify(run)

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
        socketio.emit('subscribed', {'run_id': run_id}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
