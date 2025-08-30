from celery import Celery
from flask_socketio import SocketIO
from core.models import Run
from mcp_runtime.runtime import MCPRuntime
import time
import os

# It's better to have one Celery app instance.
# We can define it here and import it in app.py if needed,
# but for now, this standalone setup is fine as long as the config is consistent.
celery = Celery('tasks', broker=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))
socketio = SocketIO(message_queue=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))

run_model = Run()

@celery.task
def execute_run(run_id, command_string=None, workflow_yaml=None):
    print(f"Executing run {run_id}")
    run_model.update(run_id, {'status': 'running'})
    socketio.emit('status', {'run_id': run_id, 'status': 'running'}, room=f'run_{run_id}')

    try:
        # Pass socketio instance to runtime for workflow communication
        runtime = MCPRuntime(socketio=socketio)

        if workflow_yaml:
            # Execute a workflow
            print(f"Executing workflow for run {run_id}")
            final_status = runtime.execute_workflow(run_id, workflow_yaml)
            run_model.update(run_id, {'status': final_status})
            socketio.emit('status', {'run_id': run_id, 'status': final_status}, room=f'run_{run_id}')
            print(f"Workflow for run {run_id} completed with status: {final_status}")

        elif command_string:
            # Execute a single command
            print(f"Executing command for run {run_id}: {command_string}")
            final_exit_code = 0
            for output in runtime.execute(command_string):
                if isinstance(output, int):
                    final_exit_code = output
                else:
                    socketio.emit('log', {'run_id': run_id, 'log': output}, room=f'run_{run_id}')
                    time.sleep(0.1)

            if final_exit_code == 0:
                run_model.update(run_id, {'status': 'succeeded'})
                socketio.emit('status', {'run_id': run_id, 'status': 'succeeded'}, room=f'run_{run_id}')
            else:
                run_model.update(run_id, {'status': 'failed', 'exit_code': final_exit_code})
                socketio.emit('status', {'run_id': run_id, 'status': 'failed', 'exit_code': final_exit_code}, room=f'run_{run_id}')
            print(f"Command for run {run_id} completed with exit code {final_exit_code}")

        else:
            raise ValueError("No command or workflow provided.")

    except Exception as e:
        print(f"Run {run_id} failed: {e}")
        run_model.update(run_id, {'status': 'failed'})
        socketio.emit('log', {'run_id': run_id, 'log': f"Runtime Error: {str(e)}"}, room=f'run_{run_id}')
        socketio.emit('status', {'run_id': run_id, 'status': 'failed'}, room=f'run_{run_id}')
