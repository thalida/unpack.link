from pprint import pprint
import json
import logging

from flask import Blueprint, request, abort, jsonify
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
        rules = request.json.get('rules')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fetcher_p1', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='fetcher_p1',
            body=json.dumps({
                'node_url': node_url,
                'rules': rules,
            }),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        return jsonify({'success': True})
    except Exception:
        return jsonify({'success': False})
