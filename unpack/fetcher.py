from pprint import pprint
import json

import pika

from .helpers import UnpackHelpers
from .types.base import TypeBase
from .types.media import TypeMedia
from .types.twitter import TypeTwitter


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
        self.rules = body.get('rules', {'max_link_depth': 2})

        self.node_url = body['node_url']
        self.node_uuid = body['node_uuid']
        self.source_node_uuid = body.get('source_node_uuid')
        self.origin_source_url = body.get('origin_source_url')

        if self.origin_source_url is None:
            self.origin_source_url = self.node_url

        self.node_url_hash = UnpackHelpers.get_url_hash(body['node_url'])
        self.is_parent_node = self.source_node_uuid is None
        self.walk_node_tree()
        ch.basic_ack(delivery_tag=method.delivery_tag)


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

        Fetcher.broadcast(
            node_url=self.node_url,
            source_node_uuid=self.source_node_uuid,
            target_node_uuid=self.node_uuid,
            origin_source_url=self.origin_source_url,
            state=self.state,
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

            origin_source_uuid = UnpackHelpers.fetch_node_uuid(self.origin_source_url)
            is_found_in_path = UnpackHelpers.check_target_node_in_path(
                origin_source_uuid,
                self.node_uuid,
                target_node_uuid
            )

            if target_url == self.node_url or is_found_in_path:
                continue

            new_state = self.state.copy()
            new_state['level'] += 1

            channel.basic_publish(
                exchange='',
                routing_key='fetcher',
                body=json.dumps({
                    'node_uuid': target_node_uuid,
                    'node_url': target_url,
                    'source_node_uuid': self.node_uuid,
                    'origin_source_url':self.origin_source_url,
                    'state': new_state,
                    'rules': self.rules,
                }),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

    @staticmethod
    def broadcast(node_url=None, source_node_uuid=None, target_node_uuid=None, origin_source_url=None, state=None):
        channel.basic_publish(
            exchange='',
            routing_key='broadcaster',
            body=json.dumps({
                'node_url': node_url,
                'source_node_uuid': source_node_uuid,
                'target_node_uuid': target_node_uuid,
                'origin_source_url': origin_source_url,
                'state': state,
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


def main():
    global channel

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='fetcher', durable=True)
    print(' [*] Waiting for Fetcher messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='fetcher', on_message_callback=Fetcher)

    channel.start_consuming()

if __name__ == '__main__':
    main()
