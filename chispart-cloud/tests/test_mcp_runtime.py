import unittest
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask
from flask_socketio import SocketIO, test_client
from app import app, socketio
from core.models import Run

class TestMCPRuntime(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.socketio = socketio
        self.client = self.app.test_client()
        self.socketio_client = self.socketio.test_client(self.app)
        time.sleep(1)

    def tearDown(self):
        self.socketio_client.disconnect()

    def test_shell_exec_success(self):
        response = self.client.post('/api/execute', json={'command': "shell.exec 'echo hello world'"})
        self.assertEqual(response.status_code, 202)
        run_id = response.json['id']

        self.socketio_client.emit('subscribe_to_run', {'run_id': run_id})
        time.sleep(5)

        received = self.socketio_client.get_received()

        logs = [msg['args'][0]['log'] for msg in received if msg['name'] == 'log' and msg['args'][0]['run_id'] == run_id]
        statuses = [msg['args'][0]['status'] for msg in received if msg['name'] == 'status' and msg['args'][0]['run_id'] == run_id]

        self.assertIn('hello world\n', logs)
        self.assertIn('succeeded', statuses)

    def test_file_write_success(self):
        write_cmd = "file.write 'test.txt' 'hello from file'"
        response = self.client.post('/api/execute', json={'command': write_cmd})
        self.assertEqual(response.status_code, 202)
        run_id_write = response.json['id']
        time.sleep(5)

        received = self.socketio_client.get_received()
        statuses = [msg['args'][0]['status'] for msg in received if msg['name'] == 'status' and msg['args'][0]['run_id'] == run_id_write]
        self.assertIn('succeeded', statuses)

if __name__ == '__main__':
    unittest.main()
