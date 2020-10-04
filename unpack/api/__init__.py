import log

import os
os.environ['TZ'] = 'UTC'

import eventlet
eventlet.monkey_patch()

import logging
import json
from flask import Flask, abort, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import pika

from helpers import UnpackHelpers

logger = logging.getLogger(__name__)

app = Flask(__name__,
            static_folder="./dist",
            template_folder="./dist")
app.url_map.strict_slashes = False
cors = CORS(app)

allowed_origin = f'http://{os.environ["UNPACK_HOST"]}:8080'
socketio = SocketIO()
socketio.init_app(app, message_queue=f'amqp://{os.environ["UNPACK_HOST"]}:5672', cors_allowed_origins=allowed_origin)

@app.route('/api/queue/create', methods=['POST'])
def queue_create():
    try:
        node_url = request.json.get('url')
        rules = request.json.get('rules')

        node_uuid = UnpackHelpers.fetch_node_uuid(node_url)
        request_id = UnpackHelpers.get_request_id(node_uuid=node_uuid)
        event_keys = UnpackHelpers.get_queue_event_keys(request_id)

        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['UNPACK_HOST']))
        channel = connection.channel()
        fetcher_queue_name = UnpackHelpers.get_queue_name(
            queue_type='fetch',
            request_id=request_id
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
            'node_url': node_url,
            'node_uuid': node_uuid,
            'request_id': request_id,
            'event_keys': event_keys,
        })
    except Exception:
        logger.exception('Error GET queue_create')
        abort(500)


@app.route('/api/queue/<string:request_id>/start', methods=['POST'])
def queue_start(request_id):
    try:
        container = UnpackHelpers.start_docker_container(
            container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_MANAGER'],
            request_id=request_id,
        )

        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['UNPACK_HOST']))
        channel = connection.channel()
        broadcaster_queue_name = UnpackHelpers.get_queue_name(
            queue_type='broadcast',
            request_id=request_id
        )
        channel.queue_declare(queue=broadcaster_queue_name)
        channel.basic_publish(
            exchange='',
            routing_key=broadcaster_queue_name,
            body=json.dumps({
                'event_name': UnpackHelpers.EVENT_NAME['REQUEST:QUEUED'],
                'data': {},
            }, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        connection.close()

        return jsonify({'container': container.id})
    except Exception as e:
        logger.exception(f'Error starting queue: {request_id}')
        abort(500)


@app.route('/api/queue/<string:request_id>/stop', methods=['POST'])
def queue_stop(request_id):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['UNPACK_HOST']))
        channel = connection.channel()
        fetcher_queue_name = UnpackHelpers.get_queue_name(
            queue_type='fetch',
            request_id=request_id
        )
        broadcaster_queue_name = UnpackHelpers.get_queue_name(
            queue_type='broadcast',
            request_id=request_id
        )
        channel.queue_delete(queue=fetcher_queue_name)
        channel.queue_delete(queue=broadcaster_queue_name)
        connection.close()

        return jsonify({'success': True})
    except Exception as e:
        logger.exception(f'Error stopping queue: {request_id}')
        abort(500)

def main():
    UnpackHelpers.get_sql_pool()
    is_debug = os.environ['UNPACK_DEV_ENV'] == 'TRUE'
    socketio.run(
        app,
        host='0.0.0.0',
        port='5000',
        debug=is_debug,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
