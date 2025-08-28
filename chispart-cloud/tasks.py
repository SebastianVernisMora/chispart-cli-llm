from celery import Celery
from flask_socketio import SocketIO
from core.models import Run
import time
import boto3
import os

celery = Celery('tasks', broker='redis://localhost:6379/0')
socketio = SocketIO(message_queue='redis://localhost:6379/0')
run_model = Run()

@celery.task
def execute_run(run_id, workflow_id):
    print(f"Executing run {run_id} for workflow {workflow_id}")
    run_model.update(run_id, {'status': 'running'})
    socketio.emit('status', {'run_id': run_id, 'status': 'running'}, room=f'run_{run_id}')

    try:
        # Simulate a long running task
        for i in range(10):
            time.sleep(1)
            socketio.emit('log', {'run_id': run_id, 'log': f'Log message {i}'}, room=f'run_{run_id}')

        # Simulate storing artifacts
        log_file = f'run_{run_id}.log'
        with open(log_file, 'w') as f:
            f.write('This is a log file.')

        # Upload to S3
        s3 = boto3.client('s3',
                          endpoint_url=os.getenv('S3_ENDPOINT_URL'),
                          aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'))

        s3.upload_file(log_file, 'my-bucket', f'runs/{run_id}/{log_file}')
        os.remove(log_file)

        run_model.update(run_id, {'status': 'succeeded'})
        socketio.emit('status', {'run_id': run_id, 'status': 'succeeded'}, room=f'run_{run_id}')
        print(f"Run {run_id} completed")
    except Exception as e:
        print(f"Run {run_id} failed: {e}")
        run_model.update(run_id, {'status': 'failed'})
        socketio.emit('status', {'run_id': run_id, 'status': 'failed'}, room=f'run_{run_id}')
