from server import socketio, app
import logging

if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    socketio.run(app)

