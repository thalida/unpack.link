import os
os.environ['TZ'] = 'UTC'

import json
import logging

from flask_socketio import SocketIO, emit

from ...helpers import UnpackHelpers
from ...content_types.twitter import ContentTypeTwitter
from ...content_types.media import ContentTypeMedia
from ...content_types.base import ContentTypeBase

logger = logging.getLogger(__name__)
socketio = SocketIO(message_queue=f'amqp://{os.environ["MQ_HOST"]}:5672')


class Broadcaster:
    def __init__(self, ch, method, properties, body):
        self.channel = ch

        body = json.loads(body)
        event_keys = UnpackHelpers.get_event_keys(
            node_url=body['origin_source_url']
        )
        event_data = {
            'origin_source_url': body['origin_source_url'],
            'state': body['state'],
            'source': None,
            'target': None,
        }

        if body['source_node_uuid']:
            event_data['source'] = {
                'node_url': UnpackHelpers.fetch_node_url(body['source_node_uuid']),
                'node_uuid': body['source_node_uuid'],
            }

        if body['target_node_uuid']:
            event_data['target'] = {
                'node_url': UnpackHelpers.fetch_node_url(body['target_node_uuid']),
                'node_uuid': body['target_node_uuid'],
            }

        logger.info(event_data['target']['node_url'])
        socketio.emit(
            event_keys['TREE_UPDATE'],
            json.dumps(event_data, default=str)
        )
