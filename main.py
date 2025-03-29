from flask import Flask, render_template, request, jsonify
import socket
import json

app = Flask(__name__)

SERVER_IP = "0.0.0.0"  # The IP address of the socket server
SERVER_PORT = 9090  # The port to communicate with the socket server

# Function to send JSON data to the socket server
def send_json_to_server(json_data):
    try:
        # Create a socket connection to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

        # Send the JSON data
        client_socket.sendall(json.dumps(json_data).encode('utf-8') + b"\r\n")

        # Optionally, receive the acknowledgment from the server
        received_data = client_socket.recv(1024).decode('utf-8')
        print(f"Received from server: {received_data}")

        client_socket.close()
    except Exception as e:
        print(f"Error sending data to server: {e}")

# API endpoint to handle form submission
@app.route('/send_data', methods=['POST'])
def send_data():
    if request.method == 'POST':
        # Get form data
        data = request.form.get('data')

        # Check if data is provided
        if data:
            try:
                # Convert form data into a dictionary and send it as JSON
                json_data = json.loads(data)
                send_json_to_server(json_data)
                return jsonify({"status": "success", "message": "Data sent to server successfully!"}), 200
            except json.JSONDecodeError:
                return jsonify({"status": "error", "message": "Invalid JSON format!"}), 400
        else:
            return jsonify({"status": "error", "message": "No data provided!"}), 400

    return render_template('index.html')  # Render the form if it's a GET request

# HTML form for data input
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
