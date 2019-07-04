import requests
import os
os.environ['TZ'] = 'UTC'

import eventlet
eventlet.monkey_patch()

import logging

from flask import Flask, abort, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from .routes import api_routes

logger = logging.getLogger(__name__)

app = Flask(__name__,
            static_folder="./dist",
            template_folder="./dist")
app.url_map.strict_slashes = False
app.register_blueprint(api_routes)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

socketio = SocketIO()
socketio.init_app(app, message_queue=f'amqp://{os.environ["UNPACK_HOST"]}:5672')

def main():
    is_debug = os.environ['UNPACK_DEV_ENV'] == 'TRUE'
    socketio.run(app, debug=is_debug, host='0.0.0.0', port='5001')

if __name__ == '__main__':
    main()
