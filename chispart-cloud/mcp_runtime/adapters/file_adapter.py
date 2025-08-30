from .base_adapter import BaseAdapter
import os
import docker
import tempfile

class FileAdapter(BaseAdapter):
    def __init__(self, runtime, image_name="mcp-exec-env:latest", working_dir="/app"):
        super().__init__(runtime)
        self.image_name = image_name
        self.docker_client = docker.from_env()
        self.working_dir = working_dir
        # Each file adapter instance gets its own temporary directory on the host
        self.host_workspace = tempfile.mkdtemp()

    def execute(self, command, *args, **kwargs):
        if command == 'write':
            return self._write_file(*args, **kwargs)
        elif command == 'read':
            return self._read_file(*args, **kwargs)
        elif command == 'list':
            return self._list_files(*args, **kwargs)
        else:
            raise ValueError(f"Unknown file command: {command}")

    def _run_in_container(self, shell_command):
        """Helper to run a command in the container with the mounted volume."""
        container = self.docker_client.containers.run(
            self.image_name,
            shell_command,
            detach=False,
            working_dir=self.working_dir,
            volumes={self.host_workspace: {'bind': self.working_dir, 'mode': 'rw'}}
        )
        return container.decode('utf-8')

    def _write_file(self, path, content):
        # To avoid command injection with content, we write the content to a temp file
        # on the host and then copy it into the container.
        # A simpler, but less secure way for now is to use echo.
        # This should be improved later to handle complex content.
        safe_path = os.path.join(self.working_dir, os.path.basename(path))
        # Use shell redirection to write the file in the container
        # Note: This approach has limitations with special characters in content.
        # A more robust solution would use Docker's API to put files in the container.
        command = f"sh -c 'echo \"{content}\" > {safe_path}'"
        self._run_in_container(command)
        return {"status": "ok", "path": safe_path}

    def _read_file(self, path):
        safe_path = os.path.join(self.working_dir, os.path.basename(path))
        command = f"cat {safe_path}"
        try:
            content = self._run_in_container(command)
            return {"status": "ok", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _list_files(self, path="."):
        safe_path = os.path.join(self.working_dir, os.path.basename(path))
        command = f"ls -la {safe_path}"
        try:
            file_list = self._run_in_container(command)
            return {"status": "ok", "files": file_list}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def __del__(self):
        # Cleanup the temporary directory when the adapter is destroyed
        import shutil
        if os.path.exists(self.host_workspace):
            shutil.rmtree(self.host_workspace)
