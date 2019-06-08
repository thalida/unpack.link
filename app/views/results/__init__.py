from pprint import pprint
import json
import logging

from flask import Blueprint, request, abort, render_template
import pika

from ...unpack.helpers import UnpackHelpers

logger = logging.getLogger(__name__)
results_view = Blueprint(
    'results_view',
    __name__,
    template_folder='../',
    static_folder='../'
)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='shard.workers', exchange_type='direct')

@results_view.route('/results', methods=['GET'])
def view():
    try:
        node_url = request.args.get('url')
        node_url_hash = UnpackHelpers.get_url_hash(node_url)
        event_keys = UnpackHelpers.get_event_keys(node_url_hash=node_url_hash)

        channel.basic_publish(
            exchange='shard.workers',
            routing_key='fetcher',
            body=json.dumps({
                'node_url': node_url,
                'rules': {'max_link_depth': 3}
            }),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        return render_template(
            'results/index.html',
            page_context={
                'EVENT_KEYS': event_keys,
                'URL_HASH': node_url_hash,
            }
        )
    except Exception:
        logger.exception('Error loading results view')
        abort(500)
