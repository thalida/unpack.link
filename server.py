import os
os.environ['TZ'] = 'UTC'

import logging
from pprint import pprint

import eventlet
eventlet.monkey_patch()

from flask import Flask, abort
from flask_socketio import SocketIO, emit

from app.views import input_view, results_view

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder = './app/views')
app.url_map.strict_slashes = False

socketio = SocketIO()
socketio.init_app(app, message_queue='redis://')

blueprints = [
    input_view,
    results_view,
]
for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socketio.run(app, debug=True, host='0.0.0.0', port='5001')
