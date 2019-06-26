import os
import json
import logging

from flask import Blueprint, request, abort, jsonify
import docker
import pika

from ..helpers import UnpackHelpers

logger = logging.getLogger(__name__)
api_routes = Blueprint(
    'unpack_api',
    __name__,
    template_folder='../',
    static_folder='../'
)

@api_routes.route('/api/event_keys', methods=['GET'])
def event_keys():
    try:
        node_url = request.args.get('url')
        event_keys = UnpackHelpers.get_event_keys(node_url=node_url)
        return jsonify(event_keys)
    except Exception:
        logger.exception('Error GET event_keys')
        abort(500)

@api_routes.route('/api/start', methods=['POST'])
def unpack():
    try:
        node_url = request.json.get('url')
        node_uuid = UnpackHelpers.fetch_node_uuid(node_url);
        rules = request.json.get('rules')

        fetcher_queue_name = f'fetch-{node_uuid}'

        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['MQ_HOST']))
        channel = connection.channel()
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

        client = docker.from_env()
        container = client.containers.run(
            image="unpack_container",
            command=f"queue-manager -q {node_uuid}",
            environment={
                'MQ_HOST': os.environ['MQ_HOST'],
                'UNPACK_DB_NAME': os.environ['UNPACK_DB_NAME'],
                'UNPACK_DB_USER': os.environ['UNPACK_DB_USER'],
                'UNPACK_DB_PASSWORD': os.getenv('UNPACK_DB_PASSWORD'),
            },
            volumes={
                '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'ro'},
                '/tmp/unpack_manager_logs.log': {'bind': '/tmp/unpack_controller_logs.log', 'mode': 'rw'},
            },
            detach=True,
            auto_remove=True,
        )

        connection.close()
        return jsonify({'success': True})
    except Exception as e:
        logger.exception(e)
        return jsonify({'success': False})
