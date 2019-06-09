import os
os.environ['TZ'] = 'UTC'

import eventlet
eventlet.monkey_patch()

import logging
from pprint import pprint

from flask import Flask, abort
from flask_socketio import SocketIO, emit

from unpack import api
from .views import input_view, results_view

def main():
    logger = logging.getLogger(__name__)
    blueprints = [
        api,
        input_view,
        results_view,
    ]

    app = Flask(__name__, static_folder = './views')
    app.url_map.strict_slashes = False

    socketio = SocketIO()
    socketio.init_app(app, message_queue='amqp://')

    for bp in blueprints:
        app.register_blueprint(bp)

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socketio.run(app, debug=True, host='0.0.0.0', port='5001')

if __name__ == '__main__':
    main()
