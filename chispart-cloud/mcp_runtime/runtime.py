import os
import importlib
from .adapters.base_adapter import BaseAdapter

class MCPRuntime:
    def __init__(self):
        self.adapters = {}
        self.load_adapters()

    def load_adapters(self):
        adapters_dir = os.path.join(os.path.dirname(__file__), 'adapters')
        for filename in os.listdir(adapters_dir):
            if filename.endswith('_adapter.py'):
                module_name = f"chispart-cloud.mcp_runtime.adapters.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name.replace('chispart-cloud.',''))
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
            # This is a simplified parsing of arguments. A more robust solution
            # would use something like shlex.
            args = [arg.strip("'\"") for arg in args_str.split()]

            adapter = self.adapters[adapter_name]
            # The execution logic will depend on whether the adapter's method is a generator
            result = adapter.execute(command, *args)
            if hasattr(result, '__iter__'):
                yield from result
            else:
                yield result
        else:
            yield f"Error: Adapter '{adapter_name}' not found."
