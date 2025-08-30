import os
import time
import boto3
from botocore.client import Config
from celery_config import celery_app
from core.models import Run
from mcp_runtime.runtime import MCPRuntime
from app import socketio, redis_client

run_model = Run()

def get_s3_client():
    """Initializes and returns a boto3 S3 client."""
    return boto3.client(
        's3',
        endpoint_url=os.environ.get('S3_ENDPOINT'),
        aws_access_key_id=os.environ.get('S3_ACCESS_KEY'),
        aws_secret_access_key=os.environ.get('S3_SECRET_KEY'),
        config=Config(signature_version='s3v4')
    )

def upload_artifacts(run_id, base_path='.'):
    """Scans for new/modified files and uploads them to S3."""
    s3 = get_s3_client()
    bucket_name = os.environ.get('S3_BUCKET', 'artifacts')
    uploaded_files = []

    for root, _, files in os.walk(base_path):
        for file in files:
            # Simple heuristic to avoid uploading .pyc files or logs
            if file.endswith(('.pyc', '.log')):
                continue

            local_path = os.path.join(root, file)
            # Avoid uploading the script itself or other project files
            if 'verify_workers.py' in local_path or 'celery_config.py' in local_path:
                continue

            s3_path = f"{run_id}/{file}"
            try:
                s3.upload_file(local_path, bucket_name, s3_path)
                uploaded_files.append(s3_path)
                print(f"Uploaded artifact {local_path} to {s3_path}")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")

    if uploaded_files:
        run_model.update(run_id, {'artifacts': uploaded_files})

@celery_app.task(
    bind=True,
    name='tasks.execute_command',
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True,
    retry_backoff_max=60
)
def execute_command(self, run_id, command_string):
    """
    Executes a shell command, streams logs, and uploads artifacts.
    Retries on failure with exponential backoff.
    """
    room = f'run_{run_id}'

    def emit_log(message):
        socketio.emit('log', {'run_id': run_id, 'log': message}, room=room)
        print(message)

    # Get the queue name from the delivery info
    queue_name = self.request.delivery_info['routing_key'].split('.')[-1]

    def emit_status(status, extra_data={}):
        payload = {'run_id': run_id, 'status': status, **extra_data}
        socketio.emit('status', payload, room=room)
        run_model.update(run_id, {'status': status, **extra_data})

        # Update metrics on final status
        if status in ['succeeded', 'failed']:
            redis_client.incr(f"metrics:queue:{queue_name}:processed")
            redis_client.incr(f"metrics:queue:{queue_name}:{status}")


    emit_log(f"Executing run {run_id} (attempt {self.request.retries + 1}/{self.request.retries_max or 3}) with command: `{command_string}` on queue `{queue_name}`")
    emit_status('running')

    try:
        runtime = MCPRuntime()
        final_exit_code = 0

        # Track files before execution to detect new ones
        files_before = set(os.listdir('.'))

        for output in runtime.execute(command_string):
            if isinstance(output, int):
                final_exit_code = output
            else:
                emit_log(output)
                time.sleep(0.1) # Prevent overwhelming the client

        emit_log("Command execution finished. Uploading artifacts...")
        upload_artifacts(run_id)

        if final_exit_code == 0:
            emit_status('succeeded')
        else:
            emit_status('failed', {'exit_code': final_exit_code})

        emit_log(f"Run {run_id} completed with exit code {final_exit_code}")
        return f"Run {run_id} completed with exit code {final_exit_code}"

    except Exception as e:
        emit_log(f"Run {run_id} failed on attempt {self.request.retries + 1}: {e}")
        # The autoretry_for logic will handle the retry
        raise
