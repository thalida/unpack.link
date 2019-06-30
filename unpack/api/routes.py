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

@api_routes.route('/api/node_event_keys', methods=['GET'])
def node_event_keys():
    try:
        node_url = request.args.get('url')
        node_event_keys = UnpackHelpers.get_node_event_keys(node_url=node_url)
        return jsonify(node_event_keys)
    except Exception:
        logger.exception('Error GET node_event_keys')
        abort(500)

@api_routes.route('/api/start', methods=['POST'])
def unpack():
    try:
        node_url = request.json.get('url')
        node_uuid = UnpackHelpers.fetch_node_uuid(node_url);
        rules = request.json.get('rules')

        fetcher_queue_name = f'fetch-{node_uuid}'

        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['UNPACK_HOST']))
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

        UnpackHelpers.start_docker_container(
            container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_MANAGER'],
            queue_name=node_uuid,
        )

        connection.close()
        return jsonify({'success': True})
    except Exception as e:
        logger.exception(e)
        return jsonify({'success': False})
