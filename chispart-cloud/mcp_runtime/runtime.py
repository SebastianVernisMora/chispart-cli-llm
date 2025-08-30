import os
import importlib
from .adapters.base_adapter import BaseAdapter
from .dag_executor import DAGExecutor

class MCPRuntime:
    def __init__(self, socketio=None):
        self.adapters = {}
        self.socketio = socketio
        self.load_adapters()

    def load_adapters(self):
        adapters_dir = os.path.join(os.path.dirname(__file__), 'adapters')
        for filename in os.listdir(adapters_dir):
            if filename.endswith('_adapter.py'):
                module_name = f"chispart-cloud.mcp_runtime.adapters.{filename[:-3]}"
                try:
                    # When running from `tasks.py`, the CWD is different.
                    # This import style is more robust.
                    module = importlib.import_module(f".adapters.{filename[:-3]}", package="mcp_runtime")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseAdapter) and attr is not BaseAdapter:
                            adapter_name = filename.replace('_adapter.py', '')
                            self.adapters[adapter_name] = attr(self)
                except ImportError as e:
                    print(f"Error importing adapter {module_name}: {e}")

    def execute(self, command_string):
        """
        Parses a command string (e.g., "shell.exec 'ls -la'") and executes it.
        Yields the output from the adapter.
        """
        parts = command_string.split(' ', 1)
        adapter_cmd = parts[0]
        args_str = parts[1] if len(parts) > 1 else ''

        adapter_name, command = adapter_cmd.split('.')

        if adapter_name in self.adapters:
            import shlex
            args = shlex.split(args_str)

            adapter = self.adapters[adapter_name]
            result = adapter.execute(command, *args)

            # Ensure we can iterate over the result
            if isinstance(result, (str, bytes, dict)):
                yield result
            elif hasattr(result, '__iter__'):
                yield from result
            else:
                yield str(result)
        else:
            yield f"Error: Adapter '{adapter_name}' not found."

    def execute_workflow(self, run_id, workflow_yaml):
        """
        Executes a DAG workflow from a YAML definition.
        """
        if not self.socketio:
            raise ValueError("SocketIO instance is required for workflow execution.")

        executor = DAGExecutor(
            runtime=self,
            run_id=run_id,
            workflow_yaml=workflow_yaml,
            socketio=self.socketio
        )
        final_status = executor.execute()
        return final_status
