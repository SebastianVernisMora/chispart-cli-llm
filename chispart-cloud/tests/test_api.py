import unittest
import json
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, run_model

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    @patch('app.execute_run.delay')
    def test_execute_command(self, mock_delay):
        command = "shell.exec 'ls -la'"
        response = self.app.post('/api/execute',
                                 data=json.dumps({'command': command}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json['command'], command)
        self.assertEqual(response.json['status'], 'queued')
        mock_delay.assert_called_once_with(response.json['id'], command)

    def test_get_runs(self):
        # Create a run first to ensure there's something to get
        run = run_model.create({'command': 'test.command', 'status': 'succeeded'})
        response = self.app.get('/runs')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertIn(run, response.json)

    def test_get_run_by_id(self):
        run = run_model.create({'command': 'test.command', 'status': 'succeeded'})
        response = self.app.get(f'/runs/{run["id"]}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, run)

if __name__ == '__main__':
    unittest.main()
