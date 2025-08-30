from celery import Celery
from flask_socketio import SocketIO
from core.models import Run
from mcp_runtime.runtime import MCPRuntime
import time
import os

celery = Celery('tasks', broker='redis://127.0.0.1:6379/0')
socketio = SocketIO(message_queue='redis://127.0.0.1:6379/0')
run_model = Run()

@celery.task
def execute_run(run_id, command_string):
    print(f"Executing run {run_id} with command: {command_string}")
    run_model.update(run_id, {'status': 'running'})
    socketio.emit('status', {'run_id': run_id, 'status': 'running'}, room=f'run_{run_id}')

    try:
        runtime = MCPRuntime()

        final_exit_code = 0
        for output in runtime.execute(command_string):
            if isinstance(output, int): # This is how we get the exit code from shell.exec
                final_exit_code = output
                # Don't send the exit code as a log message
            else:
                socketio.emit('log', {'run_id': run_id, 'log': output}, room=f'run_{run_id}')
                time.sleep(0.1) # Small delay to prevent overwhelming the client

        if final_exit_code == 0:
            run_model.update(run_id, {'status': 'succeeded'})
            socketio.emit('status', {'run_id': run_id, 'status': 'succeeded'}, room=f'run_{run_id}')
        else:
            run_model.update(run_id, {'status': 'failed', 'exit_code': final_exit_code})
            socketio.emit('status', {'run_id': run_id, 'status': 'failed', 'exit_code': final_exit_code}, room=f'run_{run_id}')

        print(f"Run {run_id} completed with exit code {final_exit_code}")

    except Exception as e:
        print(f"Run {run_id} failed: {e}")
        run_model.update(run_id, {'status': 'failed'})
        socketio.emit('log', {'run_id': run_id, 'log': f"Runtime Error: {e}"}, room=f'run_{run_id}')
        socketio.emit('status', {'run_id': run_id, 'status': 'failed'}, room=f'run_{run_id}')
