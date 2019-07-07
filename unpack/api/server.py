import requests
import os
os.environ['TZ'] = 'UTC'

import eventlet
eventlet.monkey_patch()

import logging
import json
from flask import Flask, abort, request, abort, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import pika

from ..helpers import UnpackHelpers

logger = logging.getLogger(__name__)

app = Flask(__name__,
            static_folder="./dist",
            template_folder="./dist")
app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

socketio = SocketIO()
socketio.init_app(app, message_queue=f'amqp://{os.environ["UNPACK_HOST"]}:5672')

@app.route('/api/queue/create', methods=['POST'])
def queue_create():
    try:
        node_url = request.json.get('url')
        rules = request.json.get('rules')

        node_uuid = UnpackHelpers.fetch_node_uuid(node_url)
        queue_unique_id = UnpackHelpers.get_queue_unique_id(node_uuid=node_uuid)
        event_keys = UnpackHelpers.get_queue_event_keys(queue_unique_id)

        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['UNPACK_HOST']))
        channel = connection.channel()
        fetcher_queue_name = UnpackHelpers.get_queue_name(
            queue_type='fetch',
            queue_unique_id=queue_unique_id
        )
        channel.queue_declare(queue=fetcher_queue_name)
        channel.basic_publish(
            exchange='',
            routing_key=fetcher_queue_name,
            body=json.dumps({
                'node_url': node_url,
                'rules': rules,
            }),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()

        return jsonify({
            'queue_unique_id': queue_unique_id,
            'event_keys': event_keys,
        })
    except Exception:
        logger.exception('Error GET queue_create')
        abort(500)


@app.route('/api/queue/<string:queue_uid>/start', methods=['POST'])
def queue_start(queue_uid):
    try:
        container = UnpackHelpers.start_docker_container(
            container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_MANAGER'],
            queue_unique_id=queue_uid,
        )
        return jsonify({'container': container.id})
    except Exception as e:
        logger.exception(f'Error starting queue: {queue_uid}')
        abort(500)


@app.route('/api/queue/<string:queue_uid>/stop', methods=['POST'])
def queue_stop(queue_uid):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['UNPACK_HOST']))
        channel = connection.channel()
        fetcher_queue_name = UnpackHelpers.get_queue_name(
            queue_type='fetch',
            queue_unique_id=queue_uid
        )
        broadcaster_queue_name = UnpackHelpers.get_queue_name(
            queue_type='broadcast',
            queue_unique_id=queue_uid
        )
        channel.queue_delete(queue=fetcher_queue_name)
        channel.queue_delete(queue=broadcaster_queue_name)
        connection.close()

        return jsonify({'success': True})
    except Exception as e:
        logger.exception(f'Error stopping queue: {queue_uid}')
        abort(500)


# @socketio.on('connect')
# def handle_connected():
#     logger.debug('poiuy socketio connected with other logs')
#     # logger.debug(socketio.__dict__)
#     # logger.debug(socketio.server.__dict__)
#     logger.debug(socketio.server_options['client_manager'].__dict__)
#     logger.debug('=========/////============')
#     # logger.debug(socketio..__dict__)
#     # logger.debug(json.dumps(request.args.to_dict(flat=False)))
#     # logger.debug(json.dumps({h: request.headers[h] for h in request.headers.keys()
#     #                  if h not in ['Host', 'Content-Type', 'Content-Length']}))
#     # logger.debug(json)
#     # queue_unique_id = json.get('queue_unique_id')

# @socketio.on('disconnect')
# def handle_disconnected():
#     logger.debug('qwerty socketio disconnected with json')
#     logger.debug(json.dumps(request.args.to_dict(flat=False)))
#     logger.debug(json.dumps({h: request.headers[h] for h in request.headers.keys()
#                              if h not in ['Host', 'Content-Type', 'Content-Length']}))
#     # logger.debug(json)
#     # queue_unique_id = json.get('queue_unique_id')

def main():
    is_debug = os.environ['UNPACK_DEV_ENV'] == 'TRUE'
    socketio.run(app, host='0.0.0.0', port='5000', debug=is_debug)


if __name__ == '__main__':
    main()
