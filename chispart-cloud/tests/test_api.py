import unittest
import json
from unittest.mock import patch
from app import app, socketio, workflow_model, run_model

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_create_workflow(self):
        response = self.app.post('/workflows',
                                 data=json.dumps({'name': 'test_workflow'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'test_workflow')

    def test_get_workflows(self):
        response = self.app.get('/workflows')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    @patch('app.execute_run.delay')
    def test_create_run(self, mock_delay):
        # First create a workflow
        workflow = workflow_model.create({'name': 'test_workflow'})

        response = self.app.post('/runs',
                                 data=json.dumps({'workflow_id': workflow['id']}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['workflow_id'], workflow['id'])
        self.assertEqual(response.json['status'], 'queued')
        mock_delay.assert_called_once_with(response.json['id'], workflow['id'])

    def test_get_runs(self):
        response = self.app.get('/runs')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

if __name__ == '__main__':
    unittest.main()
