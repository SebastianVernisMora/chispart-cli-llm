from flask import Flask, request, jsonify
import subprocess  # Import subprocess for executing commands

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return app.send_static_file('chat_interface.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.json.get('command')  # Get the command from the request
    print(f"Received command: {command}")  # Log the received command
    if command:
        try:
            # Simulate an AI response
            ai_response = f"You said: {command}"
            return jsonify({
                'stdout': ai_response,
                'stderr': '',
                'returncode': 0
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'No command provided'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
