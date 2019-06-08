from pprint import pprint
import json

import pika
from flask_socketio import SocketIO, emit

from app.unpack.helpers import UnpackHelpers
from app.unpack.types.base import TypeBase
from app.unpack.types.media import TypeMedia
from app.unpack.types.twitter import TypeTwitter

socketio = SocketIO(message_queue='amqp://')

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='shard.workers', exchange_type='direct')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='shard.workers', queue=queue_name, routing_key='broadcaster')
print(' [*] Waiting for Broadcaster messages. To exit press CTRL+C')

class Broadcaster:
    def __init__(self, ch, method, properties, body):
        body = json.loads(body)
        event_keys = UnpackHelpers.get_event_keys(node_uuid=body['origin_source_node_uuid'])
        print(event_keys)
        print('before broadcast')
        socketio.emit(event_keys['TREE_UPDATE'], json.dumps(body, default=str))
        print('after socket broadcast')


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=Broadcaster, auto_ack=True)

channel.start_consuming()
