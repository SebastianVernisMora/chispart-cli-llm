import socketio
import requests
import time

# Client configuration
SERVER_URL = "http://localhost:8080"
USER_ID = "test-user-123"

# Standard python-socketio client
sio = socketio.Client()

@sio.event
def connect():
    print("Connection established")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on('connection_response')
def on_connection_response(data):
    print(f"Server connection response: {data}")
    # Now that we are connected, send a command
    test_command = "!ls -l"
    print(f"\nSending command: '{test_command}'")
    sio.emit('shell_command', {'command': test_command})

@sio.on('shell_response')
def on_shell_response(data):
    print(f"Received shell response:")
    print(data.get('output', 'No output received.'))
    # Give a moment before disconnecting
    time.sleep(1)
    sio.disconnect()

def run_client():
    # 1. Get a token
    try:
        response = requests.get(f"{SERVER_URL}/get-token/{USER_ID}")
        response.raise_for_status()
        token = response.json()['token']
        print(f"Successfully obtained token: {token[:30]}...")
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        return

    # 2. Connect to the WebSocket server with the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        sio.connect(SERVER_URL, headers=headers)
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    run_client()
