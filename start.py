from server import socketio, app
import logging
import os

if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    port = os.environ.get('PORT', 5000)
    socketio.run(app, port=int(port))

