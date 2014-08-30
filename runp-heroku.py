from server import app, socketio
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)

socketio.run(app)
