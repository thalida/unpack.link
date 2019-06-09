import os
os.environ['TZ'] = 'UTC'

import eventlet
eventlet.monkey_patch()

import logging
from pprint import pprint

from flask import Flask, abort, render_template
from flask_socketio import SocketIO, emit

from .routes import api_routes

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(api_routes)

socketio = SocketIO()
socketio.init_app(app, message_queue='amqp://')


def main():
    socketio.run(app, debug=True, host='0.0.0.0', port='5001')

if __name__ == '__main__':
    main()
