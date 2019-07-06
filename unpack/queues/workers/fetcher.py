import os
os.environ['TZ'] = 'UTC'

import logging
logger = logging.getLogger(__name__)

import json

import pika
from redis import Redis

from ...helpers import UnpackHelpers
from ...content_types.twitter import ContentTypeTwitter
from ...content_types.media import ContentTypeMedia
from ...content_types.website import ContentTypeWebsite

r = Redis(host=os.environ['UNPACK_HOST'])

class Fetcher:
    NODE_TYPES = [
        ContentTypeTwitter(),
        ContentTypeMedia(),

        # TypeBase should always be last
        ContentTypeWebsite(),
    ]

    DEFAULT_STATE = {
        'level': 0,
    }

    DEFAULT_RULES = {
        'force_from_web': False,
        'force_from_db': False,
        'max_link_depth': 2,
        'twitter_use_max_link_depth': False,
    }

    def __init__(self, ch, method, properties, body):
        self.channel = ch
        self.queue_unique_id = UnpackHelpers.get_queue_unique_id_from_name(method.routing_key)

        body = json.loads(body)

        if body.get('node_uuid') is None:
            body['node_uuid'] = UnpackHelpers.fetch_node_uuid(body.get('node_url'))

        if body.get('node_url') is None:
            body['node_url'] = UnpackHelpers.fetch_node_url(body.get('node_uuid'))

        state = body.get('state', {})
        self.state = {**self.DEFAULT_STATE, **state}

        rules = body.get('rules', {})
        rules = {} if rules is None else rules
        self.rules = {**self.DEFAULT_RULES, **rules}

        self.node_url = body['node_url']
        self.node_uuid = body['node_uuid']
        self.node_url_hash = UnpackHelpers.get_url_hash(body['node_url'])

        self.source_node_uuid = body.get('source_node_uuid')
        self.origin_source_node_url = body.get('origin_source_node_url', self.node_url)
        self.origin_source_uuid = UnpackHelpers.fetch_node_uuid(self.origin_source_node_url)
        self.is_origin_node = self.source_node_uuid is None

        self.publish_broadcast(
            event_name=UnpackHelpers.EVENT_NAME['FETCH:NODE:IN_PROGRESS'],
            node_uuid=self.node_uuid,
            node_url=self.node_url,
        )

        self.walk_node_tree()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def walk_node_tree(self):
        if self.node_url is None:
            return

        type_cls, node_url_match = Fetcher.get_node_type_class_by_url(self.node_url)
        node_metadata, raw_links = type_cls.fetch(
            self.node_uuid,
            self.node_url,
            url_matches=node_url_match,
            rules=self.rules
        )

        has_links = len(raw_links) > 0

        if not node_metadata.get('is_from_db', True):
            UnpackHelpers.store_node_metadata(
                self.node_uuid,
                node_type=node_metadata.get('node_type'),
                data=node_metadata.get('data'),
                is_error=node_metadata.get('is_error'),
            )

        self.publish_broadcast(
            event_name=UnpackHelpers.EVENT_NAME['FETCH:NODE:COMPLETED'],
            node_uuid=self.node_uuid,
            node_url=self.node_url,
            node_metadata=node_metadata,
        )

        if not has_links:
            UnpackHelpers.store_link(self.node_uuid)
            return

        self.process_links(
            raw_links=raw_links,
            type_cls=type_cls,
        )

    def process_links(self, raw_links, type_cls):
        has_reached_max_depth = self.state['level'] + 1 > self.rules['max_link_depth']

        if has_reached_max_depth:
            if type_cls.TYPE != 'twitter':
                return
            elif self.rules['twitter_use_max_link_depth']:
                return

        for raw_link in raw_links:
            link_type = raw_link.get('link_type')
            if has_reached_max_depth and link_type in ['media', 'link']:
                continue

            source_node_url = self.node_url
            source_node_uuid = self.node_uuid
            target_node_url = raw_link.get('target_node_url')
            target_node_uuid = raw_link.get('target_node_uuid')

            if not target_node_uuid and target_node_url:
                target_node_uuid = UnpackHelpers.fetch_node_uuid(target_node_url)

            if not target_node_url and target_node_uuid:
                target_node_url = UnpackHelpers.fetch_node_url(target_node_uuid)

            if not target_node_uuid or not target_node_url:
                continue

            self.store_link(
                source_node_url=source_node_url,
                source_node_uuid=source_node_uuid,
                target_node_url=target_node_url,
                target_node_uuid=target_node_uuid,
                raw_link=raw_link,
            )

            self.queue_next_node(
                source_node_url=source_node_url,
                source_node_uuid=source_node_uuid,
                target_node_url=target_node_url,
                target_node_uuid=target_node_uuid
            )
    def store_link(self, source_node_url, source_node_uuid, target_node_url, target_node_uuid, raw_link):
        UnpackHelpers.store_link(
            source_node_uuid,
            target_node_uuid=target_node_uuid,
            link_type=raw_link.get('link_type'),
            weight=raw_link.get('weight'),
        )

        self.publish_broadcast(
            event_name=UnpackHelpers.EVENT_NAME['STORE:LINK:COMPLETED'],
            source_node_url=source_node_url,
            source_node_uuid=source_node_uuid,
            target_node_url=target_node_url,
            target_node_uuid=target_node_uuid,
            link_type=raw_link.get('link_type'),
            weight=raw_link.get('weight'),
        )

    def queue_next_node(self, source_node_url, source_node_uuid, target_node_url, target_node_uuid):
        if target_node_url == source_node_url:
            return

        cache_key = f'{self.queue_unique_id}:{target_node_uuid}'

        if r.exists(cache_key):
            return

        new_fetcher_state = self.state.copy()
        new_fetcher_state['level'] += 1

        self.publish_broadcast(
            event_name=UnpackHelpers.EVENT_NAME['FETCH:NODE:QUEUED'],
            node_uuid=target_node_uuid,
            node_url=target_node_url,
        )

        self.publish_child({
            'node_uuid': target_node_uuid,
            'node_url': target_node_url,
            'source_node_uuid': source_node_uuid,
            'origin_source_node_url': self.origin_source_node_url,
            'state': new_fetcher_state,
            'rules': self.rules,
        })

        r.set(cache_key, 'true', ex=10 * 60)

    def publish_broadcast(self, event_name, **kwargs):
        queue_name = UnpackHelpers.get_queue_name('broadcast', self.queue_unique_id)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps({
                'event_name': event_name,
                'origin_source_node_url': self.origin_source_node_url,
                'data': kwargs,
            }, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def publish_child(self, body):
        queue_name = UnpackHelpers.get_queue_name('fetch', self.queue_unique_id)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    @staticmethod
    def get_node_type_class_by_url(node_url):
        type_cls = None
        node_match = None

        for url_type in Fetcher.NODE_TYPES:
            try:
                matches = url_type.URL_PATTERN.findall(node_url)
                if len(matches) > 0:
                    type_cls = url_type
                    node_match = matches[0]
                    break
            except TypeError as e:
                logger.exception(node_url, e)

        return type_cls, node_match
