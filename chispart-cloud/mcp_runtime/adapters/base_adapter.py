class BaseAdapter:
    def __init__(self, runtime):
        self.runtime = runtime

    def execute(self, command, *args, **kwargs):
        raise NotImplementedError
