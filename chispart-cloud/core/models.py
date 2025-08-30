import json
from pathlib import Path

class Model:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "db.json"
        self._db = self._load_db()

    def _load_db(self):
        if not self.db_path.exists():
            self.db_path.touch()
            self.db_path.write_text(json.dumps({"workflows": [], "runs": [], "tasks": []}))

        with open(self.db_path, 'r+') as f:
            db_content = json.load(f)
            if "tasks" not in db_content:
                db_content["tasks"] = []
                f.seek(0)
                json.dump(db_content, f, indent=4)
                f.truncate()

        return db_content

    def _save_db(self):
        self.db_path.write_text(json.dumps(self._db, indent=4))

    def _get_all(self, model_name):
        return self._db.get(model_name, [])

    def _get_by_id(self, model_name, id):
        for item in self._get_all(model_name):
            if item.get("id") == id:
                return item
        return None

    def _create(self, model_name, data):
        all_items = self._get_all(model_name)
        data["id"] = len(all_items) + 1 if all_items else 1
        self._db[model_name].append(data)
        self._save_db()
        return data

    def _update(self, model_name, id, data):
        for item in self._get_all(model_name):
            if item.get("id") == id:
                item.update(data)
                self._save_db()
                return item
        return None

class Workflow(Model):
    def get_all(self):
        return self._get_all("workflows")

    def get_by_id(self, id):
        return self._get_by_id("workflows", id)

    def create(self, data):
        return self._create("workflows", data)

class Run(Model):
    def get_all(self):
        return self._get_all("runs")

    def get_by_id(self, id):
        return self._get_by_id("runs", id)

    def create(self, data):
        return self._create("runs", data)

    def update(self, id, data):
        return self._update("runs", id, data)

class Task(Model):
    def get_all(self):
        return self._get_all("tasks")

    def get_by_id(self, id):
        return self._get_by_id("tasks", id)

    def create(self, data):
        if 'status' not in data:
            data['status'] = 'pending'
        return self._create("tasks", data)

    def update(self, id, data):
        return self._update("tasks", id, data)

    def find_by_run_id(self, run_id):
        return [task for task in self.get_all() if task.get("run_id") == run_id]
