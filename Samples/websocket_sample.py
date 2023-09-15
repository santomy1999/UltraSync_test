from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    print(f'Received message: {message}')
    # Process the message as needed
    # Send a response if necessary
    socketio.emit('response', 'Response from server')

if __name__ == '__main__':
    socketio.run(app, debug=True)
