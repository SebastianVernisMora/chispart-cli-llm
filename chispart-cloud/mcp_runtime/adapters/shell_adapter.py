import docker
from .base_adapter import BaseAdapter
import os

class ShellAdapter(BaseAdapter):
    def __init__(self, runtime, image_name="mcp-exec-env:latest", working_dir="/app"):
        super().__init__(runtime)
        self.image_name = image_name
        self.docker_client = docker.from_env()
        self.working_dir = working_dir

        # Build the image if it doesn't exist
        try:
            self.docker_client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            print(f"Building Docker image: {self.image_name}")
            dockerfile_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Dockerfile.exec')
            self.docker_client.images.build(
                path=os.path.dirname(dockerfile_path),
                dockerfile=os.path.basename(dockerfile_path),
                tag=self.image_name,
                rm=True
            )

    def execute(self, command, *args, **kwargs):
        """
        Executes a shell command inside a new Docker container.
        Streams the output in real-time.
        """

        container = self.docker_client.containers.run(
            self.image_name,
            command,
            detach=True,
            working_dir=self.working_dir,
            # Mount a volume for file access if needed in the future
            # volumes={...}
        )

        for log in container.logs(stream=True, follow=True):
            yield log.decode('utf-8')

        result = container.wait()
        exit_code = result['StatusCode']

        # Clean up the container
        container.remove()

        return exit_code
