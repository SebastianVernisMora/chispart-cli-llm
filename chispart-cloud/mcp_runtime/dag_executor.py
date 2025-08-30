import yaml
import time
from threading import Thread, Event
from typing import TYPE_CHECKING
from core.models import Task

if TYPE_CHECKING:
    from mcp_runtime.runtime import MCPRuntime

class DAGExecutor:
    def __init__(self, runtime: "MCPRuntime", run_id: int, workflow_yaml: str, socketio):
        self.runtime = runtime
        self.run_id = run_id
        self.workflow_def = yaml.safe_load(workflow_yaml)
        self.socketio = socketio
        self.task_model = Task()
        self.tasks = {}
        self.task_states = {}
        self.stop_event = Event()

    def execute(self):
        # 1. Parse workflow and create tasks in DB
        self._initialize_tasks()

        # 2. Build dependency graph
        adj, in_degree = self._build_graph()

        # 3. Find initial tasks (in-degree 0)
        queue = [name for name, degree in in_degree.items() if degree == 0]

        # 4. Execute tasks in topological order
        while queue:
            task_name = queue.pop(0)

            if self.stop_event.is_set():
                self._update_task_status(task_name, 'skipped', log_message="Workflow was stopped.")
                continue

            # Check 'if' condition
            if not self._check_condition(task_name):
                self._update_task_status(task_name, 'skipped')
                # Add children to the queue
                self._process_next_tasks(task_name, adj, in_degree, queue)
                continue

            # Execute the task in a separate thread for timeout handling
            self._execute_task_with_timeout(task_name)

            # If task failed, stop the workflow
            if self.task_states[task_name]['status'] == 'failed':
                self.stop_event.set()
                # Don't break, let other tasks be marked as skipped

            # Add children to the queue
            self._process_next_tasks(task_name, adj, in_degree, queue)

        # 5. Finalize workflow status
        final_status = 'succeeded'
        for state in self.task_states.values():
            if state['status'] == 'failed':
                final_status = 'failed'
                break

        return final_status

    def _initialize_tasks(self):
        for task_def in self.workflow_def.get('tasks', []):
            task_name = task_def['name']
            db_task = self.task_model.create({
                'run_id': self.run_id,
                'name': task_name,
                'command': task_def['command'],
                'status': 'pending',
            })
            self.tasks[task_name] = db_task
            self.task_states[task_name] = {'status': 'pending'}

    def _build_graph(self):
        tasks = self.workflow_def.get('tasks', [])
        task_names = [t['name'] for t in tasks]
        adj = {name: [] for name in task_names}
        in_degree = {name: 0 for name in task_names}

        for task in tasks:
            name = task['name']
            for dep in task.get('dependencies', []):
                if dep in task_names:
                    adj[dep].append(name)
                    in_degree[name] += 1
        return adj, in_degree

    def _check_condition(self, task_name):
        task_def = self._get_task_def(task_name)
        condition = task_def.get('if')
        if not condition:
            return True

        try:
            # Create a context for eval with previous task states
            context = {'tasks': {}}
            for name, state in self.task_states.items():
                 context['tasks'][name] = {'status': state.get('status', 'pending')}
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            self._update_task_status(task_name, 'failed', log_message=f"Condition eval error: {e}")
            return False

    def _execute_task_with_timeout(self, task_name):
        task_def = self._get_task_def(task_name)
        command = task_def['command']
        retries = task_def.get('retries', 0)
        timeout = task_def.get('timeout')

        attempt = 0
        while attempt <= retries:
            self._update_task_status(task_name, 'running', attempt=attempt + 1)

            exec_thread = Thread(target=self._run_command, args=(task_name, command))
            exec_thread.start()
            exec_thread.join(timeout)

            if exec_thread.is_alive():
                self._update_task_status(task_name, 'failed', log_message=f"Timeout after {timeout}s")

            if self.task_states[task_name]['status'] == 'succeeded':
                return

            attempt += 1
            if attempt <= retries:
                self._log(task_name, f"Retrying ({attempt}/{retries})...")

    def _run_command(self, task_name, command):
        try:
            exit_code = 0
            for output in self.runtime.execute(command):
                if isinstance(output, int):
                    exit_code = output
                else:
                    self._log(task_name, output)

            if exit_code == 0:
                self._update_task_status(task_name, 'succeeded', exit_code=exit_code)
            else:
                self._update_task_status(task_name, 'failed', exit_code=exit_code, log_message=f"Command failed with exit code {exit_code}")

        except Exception as e:
            self._update_task_status(task_name, 'failed', log_message=str(e))

    def _process_next_tasks(self, completed_task_name, adj, in_degree, queue):
        # Only proceed if the task was successful or skipped
        if self.task_states[completed_task_name]['status'] not in ['succeeded', 'skipped']:
            return

        for neighbor in adj[completed_task_name]:
            # Before decrementing, check if all dependencies of the neighbor are complete
            neighbor_def = self._get_task_def(neighbor)
            all_deps_done = True
            for dep_name in neighbor_def.get('dependencies', []):
                if self.task_states[dep_name]['status'] not in ['succeeded', 'skipped']:
                    all_deps_done = False
                    break

            if all_deps_done:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    def _get_task_def(self, task_name):
        for task in self.workflow_def.get('tasks', []):
            if task['name'] == task_name:
                return task
        return None

    def _update_task_status(self, task_name, status, exit_code=None, log_message=None, attempt=None):
        task_id = self.tasks[task_name]['id']
        update_data = {'status': status}
        if exit_code is not None:
            update_data['exit_code'] = exit_code
        if attempt is not None:
            update_data['attempt'] = attempt

        self.task_model.update(task_id, update_data)
        self.task_states[task_name]['status'] = status

        self.socketio.emit('task_status', {
            'run_id': self.run_id,
            'task_id': task_id,
            'task_name': task_name,
            'status': status
        }, room=f'run_{self.run_id}')

        if log_message:
            self._log(task_name, log_message)

    def _log(self, task_name, message):
        task_id = self.tasks[task_name]['id']
        self.socketio.emit('task_log', {
            'run_id': self.run_id,
            'task_id': task_id,
            'task_name': task_name,
            'log': message
        }, room=f'run_{self.run_id}')
        # In a real system, you'd append logs to the DB record
        # For this example, we just emit them.
