import os
import redis
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, join_room
from core.models import Run, Workflow
from celery_config import celery_app, task_routes

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, message_queue=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))

# Initialize Redis client for metrics
redis_client = redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))

# Initialize models
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
    # Default to 'shell' queue if not specified
    queue = data.get('queue', 'shell')

    # Basic validation to ensure the queue exists
    if queue not in [q.name for q in celery_app.conf.task_queues]:
        return jsonify({"error": f"Invalid queue: {queue}"}), 400

    task_name = 'tasks.execute_command'

    run_data = {
        'workflow_id': data.get('workflow_id', None),
        'status': 'queued',
        'command': command_string,
        'queue': queue
    }
    new_run = run_model.create(run_data)

    # Increment the 'submitted' metric for the queue
    redis_client.incr(f"metrics:queue:{queue}:submitted")

    # Trigger the background task in the specified queue
    celery_app.send_task(
        task_name,
        args=[new_run['id'], command_string],
        queue=queue
    )

    return jsonify(new_run), 202

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

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Returns metrics for each queue."""
    metrics = {}
    # Find all keys related to queue metrics
    for key in redis_client.scan_iter("metrics:queue:*"):
        queue_name = key.decode('utf-8').split(':')[2]
        metric_type = key.decode('utf-8').split(':')[3]
        if queue_name not in metrics:
            metrics[queue_name] = {}
        metrics[queue_name][metric_type] = int(redis_client.get(key))
    return jsonify(metrics)

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
