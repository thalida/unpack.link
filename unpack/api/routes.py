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

@api_routes.route('/api/queue/create', methods=['POST'])
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


@api_routes.route('/api/queue/<string:queue_uid>/start', methods=['POST'])
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


@api_routes.route('/api/queue/<string:queue_uid>/stop', methods=['POST'])
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
