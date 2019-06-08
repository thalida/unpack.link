from pprint import pprint
import json

import pika

from app.unpack.helpers import UnpackHelpers
from app.unpack.types.base import TypeBase
from app.unpack.types.media import TypeMedia
from app.unpack.types.twitter import TypeTwitter


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='shard.workers', exchange_type='direct')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='shard.workers', queue=queue_name, routing_key='fetcher')
print(' [*] Waiting for Fetcher messages. To exit press CTRL+C')


class Fetcher:
    NODE_TYPES = [
        TypeTwitter(),
        TypeMedia(),

        # TypeBase should always be last
        TypeBase(),
    ]

    def __init__(self, ch, method, properties, body):
        body = json.loads(body)

        if body.get('node_uuid') is None:
            body['node_uuid'] = UnpackHelpers.fetch_node_uuid(body.get('node_url'))

        if body.get('node_url') is None:
            body['node_url'] = UnpackHelpers.fetch_node_url(body.get('node_uuid'))

        self.state = body.get('state', {'level': 0})
        self.rules = body.get('rules', {'max_link_depth': 5})
        self.node_uuid = body['node_uuid']
        self.node_url = body['node_url']
        self.source_node_uuid = body.get('source_node_uuid', None)
        self.origin_source_node_uuid = body.get('origin_source_node_uuid', self.node_uuid)

        self.node_url_hash = UnpackHelpers.get_url_hash(body['node_url'])
        self.is_parent_node = self.source_node_uuid is None

        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.walk_node_tree()


    def walk_node_tree(self):
        type_cls, node_url_match = Fetcher.get_node_type_class_by_url(self.node_url)
        node_details, raw_links = type_cls.fetch(self.node_uuid, self.node_url, url_matches=node_url_match)

        if not node_details.get('is_from_db', True):
            UnpackHelpers.store_node_metadata(
                self.node_uuid,
                node_type=node_details.get('node_type'),
                data=node_details.get('data'),
                is_error=node_details.get('is_error'),
            )

        print(self.node_url, self.node_uuid)
        Fetcher.broadcast(
            node_details,
            node_uuid=self.node_uuid,
            node_url=self.node_url,
            source_node_uuid=self.source_node_uuid,
            origin_source_node_uuid=self.origin_source_node_uuid,
        )

        if node_details['num_branches'] == 0:
            UnpackHelpers.store_link(self.node_uuid)
            return

        if self.state['level'] + 1 > self.rules['max_link_depth']:
            return

        for raw_link in raw_links:
            target_url = raw_link.get('target_node_url')
            target_node_uuid = raw_link.get('target_node_uuid')

            if not target_node_uuid:
                target_node_uuid = UnpackHelpers.fetch_node_uuid(target_url)

            UnpackHelpers.store_link(
                self.node_uuid,
                target_node_uuid=target_node_uuid,
                link_type=raw_link.get('link_type'),
                weight=1,
            )

            new_state = self.state.copy()
            new_state['level'] += 1

            channel.basic_publish(
                exchange='shard.workers',
                routing_key='fetcher',
                body=json.dumps({
                    'node_uuid': target_node_uuid,
                    'node_url': target_url,
                    'source_node_uuid': self.node_uuid,
                    'origin_source_node_uuid':self.origin_source_node_uuid,
                    'state': new_state,
                    'rules': self.rules,
                }),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

    @staticmethod
    def broadcast(node_details, node_uuid=None, node_url=None, source_node_uuid=None, origin_source_node_uuid=None):
        channel.basic_publish(
            exchange='shard.workers',
            routing_key='broadcaster',
            body=json.dumps({
                'node_uuid': node_uuid,
                'node_url': node_url,
                'source_node_uuid': source_node_uuid,
                'origin_source_node_uuid': origin_source_node_uuid,
                'node_details': node_details,
            }, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    @staticmethod
    def get_node_type_class_by_url(node_url):
        for url_type in Fetcher.NODE_TYPES:
            matches = url_type.URL_PATTERN.findall(node_url)
            if len(matches) > 0:
                type_cls = url_type
                node_match = matches[0]
                break

        return type_cls, node_match


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=Fetcher, auto_ack=False)

channel.start_consuming()
