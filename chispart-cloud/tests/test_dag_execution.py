import unittest
import time
import sys
import os
import json

# Set the testing flag before importing the app
os.environ['FLASK_TESTING'] = 'True'

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, socketio
from core.models import Run, Task

class TestDAGExecution(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.socketio = socketio
        self.client = self.app.test_client()

        self.socketio_client = self.socketio.test_client(self.app)
        # No need to connect manually, it's done on first emit

        # Load the demo workflow
        workflow_path = os.path.join(os.path.dirname(__file__), '..', 'demo_workflow.yml')
        with open(workflow_path, 'r') as f:
            self.workflow_yaml = f.read()

    def tearDown(self):
        if self.socketio_client.is_connected():
            self.socketio_client.disconnect()
        # Clean up the db.json file
        db_path = os.path.join(os.path.dirname(__file__), '..', 'db.json')
        if os.path.exists(db_path):
            with open(db_path, 'w') as f:
                json.dump({"workflows": [], "runs": [], "tasks": []}, f)


    def test_workflow_execution_and_failure(self):
        """
        Tests the end-to-end execution of the demo workflow, which is designed to fail.
        """
        # Since tasks run eagerly, the HTTP request will not return until the workflow is complete.
        # This simplifies the test as we don't need to wait.
        response = self.client.post('/api/execute', json={'workflow': self.workflow_yaml})
        self.assertEqual(response.status_code, 202)
        run_id = response.json['id']
        self.assertIsNotNone(run_id)

        # Get all received messages
        received = self.socketio_client.get_received()

        task_statuses = {}
        for msg in received:
            if msg['name'] == 'task_status':
                args = msg['args'][0]
                if args['run_id'] == run_id:
                    task_statuses[args['task_name']] = args['status']

        # Check the status of each task from the websocket messages
        self.assertEqual(task_statuses.get('plan'), 'succeeded')
        self.assertEqual(task_statuses.get('build'), 'succeeded')
        self.assertEqual(task_statuses.get('qa-gate'), 'succeeded')
        self.assertEqual(task_statuses.get('run-integration-tests'), 'succeeded')
        self.assertEqual(task_statuses.get('run-security-scan'), 'failed')

        # Check the DB for the final status of the skipped task
        task_model = Task()
        tasks = task_model.find_by_run_id(run_id)
        pr_task = next((t for t in tasks if t['name'] == 'create-pull-request'), None)
        self.assertIsNotNone(pr_task)
        self.assertEqual(pr_task['status'], 'skipped')

        # Check the final run status from the DB
        run_model = Run()
        final_run = run_model.get_by_id(run_id)
        self.assertEqual(final_run['status'], 'failed')

if __name__ == '__main__':
    unittest.main()
