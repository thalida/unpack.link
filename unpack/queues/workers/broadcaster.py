import os
os.environ['TZ'] = 'UTC'

import json
import logging

from flask_socketio import SocketIO, emit

from ...helpers import UnpackHelpers

logger = logging.getLogger(__name__)
socketio = SocketIO(message_queue=f'amqp://{os.environ["UNPACK_HOST"]}:5672')


class Broadcaster:
    def __init__(self, ch, method, properties, body):
        self.channel = ch

        body = json.loads(body)
        event_name = body['event_name']

        node_event_keys = UnpackHelpers.get_node_event_keys(
            node_url_hash=None,
            node_url=body['origin_source_url'],
        )

        socketio.emit(
            node_event_keys[event_name],
            json.dumps(body, default=str)
        )
