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
        request_id = UnpackHelpers.get_request_id_from_name(method.routing_key)
        queue_event_keys = UnpackHelpers.get_queue_event_keys(request_id)

        body = json.loads(body)
        event_name = body['event_name']

        socketio.emit(
            queue_event_keys[event_name],
            body['data'],
            namespace=f'/{request_id}',
        )
