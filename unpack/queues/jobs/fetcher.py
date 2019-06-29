import os
os.environ['TZ'] = 'UTC'

import json
import logging

import pika

from ...helpers import UnpackHelpers
from ...content_types.twitter import ContentTypeTwitter
from ...content_types.media import ContentTypeMedia
from ...content_types.base import ContentTypeBase

logger = logging.getLogger(__name__)


class Fetcher:
    NODE_TYPES = [
        ContentTypeTwitter(),
        ContentTypeMedia(),

        # TypeBase should always be last
        ContentTypeBase(),
    ]

    DEFAULT_STATE = {
        'level': 0,
        'weight': 0,
        'is_already_in_path': False,
    }

    DEFAULT_RULES = {
        'force_from_web': False,
        'force_from_db': False,
        'max_link_depth': 2,
    }

    def __init__(self, ch, method, properties, body):
        self.channel = ch

        body = json.loads(body)

        if body.get('node_uuid') is None:
            body['node_uuid'] = UnpackHelpers.fetch_node_uuid(
                body.get('node_url'))

        if body.get('node_url') is None:
            body['node_url'] = UnpackHelpers.fetch_node_url(
                body.get('node_uuid'))

        state = body.get('state', {})
        self.state = {**self.DEFAULT_STATE, **state}

        rules = body.get('rules', {})
        rules = {} if rules is None else rules
        self.rules = {**self.DEFAULT_RULES, **rules}

        self.node_url = body['node_url']
        self.node_uuid = body['node_uuid']
        self.node_url_hash = UnpackHelpers.get_url_hash(body['node_url'])

        self.source_node_uuid = body.get('source_node_uuid')
        self.origin_source_url = body.get('origin_source_url', self.node_url)
        self.origin_source_uuid = UnpackHelpers.fetch_node_uuid(self.origin_source_url)
        self.is_origin_node = self.source_node_uuid is None

        self.walk_node_tree()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def walk_node_tree(self):
        if self.node_url is None:
            return

        type_cls, node_url_match = Fetcher.get_node_type_class_by_url(
            self.node_url)
        node_details, raw_links = type_cls.fetch(
            self.node_uuid,
            self.node_url,
            url_matches=node_url_match,
            rules=self.rules
        )

        has_links = len(raw_links) > 0
        has_reached_max_depth = self.state['level'] + \
            1 > self.rules['max_link_depth']

        if not node_details.get('is_from_db', True):
            UnpackHelpers.store_node_metadata(
                self.node_uuid,
                node_type=node_details.get('node_type'),
                data=node_details.get('data'),
                is_error=node_details.get('is_error'),
            )

        self.broadcast(
            event_name=UnpackHelpers.EVENT_NAME['LINK_FETCH_SUCCESS'],
            source_node_uuid=self.source_node_uuid,
            target_node_uuid=self.node_uuid,
            data=self.state,
        )

        if not has_links:
            UnpackHelpers.store_link(self.node_uuid)
        elif not has_reached_max_depth:
            self.fetch_links(raw_links)

        if not self.is_origin_node:
            UnpackHelpers.remove_active_job(
                self.source_node_uuid,
                self.node_uuid
            )

    def fetch_links(self, raw_links):
        for raw_link in raw_links:
            source_url = self.node_url
            source_node_uuid = self.node_uuid
            target_url = raw_link.get('target_node_url')
            target_node_uuid = raw_link.get('target_node_uuid')

            if not target_node_uuid:
                target_node_uuid = UnpackHelpers.fetch_node_uuid(target_url)

            self.broadcast(
                event_name=UnpackHelpers.EVENT_NAME['LINK_FETCH_START'],
                source_node_uuid=source_node_uuid,
                target_node_uuid=target_node_uuid,
            )

            UnpackHelpers.store_link(
                source_node_uuid,
                target_node_uuid=target_node_uuid,
                link_type=raw_link.get('link_type'),
                weight=raw_link.get('weight', self.DEFAULT_STATE['weight']),
            )

            new_fetcher_state = self.state.copy()
            new_fetcher_state['level'] += 1
            new_fetcher_state['weight'] = raw_link.get('weight')

            if target_url == source_url:
                new_fetcher_state['is_already_in_path'] = True
                self.broadcast(
                    event_name=UnpackHelpers.EVENT_NAME['LINK_FETCH_SUCCESS'],
                    source_node_uuid=source_node_uuid,
                    target_node_uuid=target_node_uuid,
                    data=new_fetcher_state,
                )
                continue

            is_found_in_tree = UnpackHelpers.check_target_node_in_tree(
                self.origin_source_uuid,
                target_node_uuid,
                new_fetcher_state['level'],
                min_count=2
            )
            if is_found_in_tree:
                new_fetcher_state['is_already_in_path'] = True
                self.broadcast(
                    event_name=UnpackHelpers.EVENT_NAME['LINK_FETCH_SUCCESS'],
                    source_node_uuid=source_node_uuid,
                    target_node_uuid=target_node_uuid,
                    data=new_fetcher_state,
                )
                continue

            UnpackHelpers.store_active_job(source_node_uuid, target_node_uuid)
            self.publish_child({
                'node_uuid': target_node_uuid,
                'node_url': target_url,
                'source_node_uuid': source_node_uuid,
                'origin_source_url': self.origin_source_url,
                'state': new_fetcher_state,
                'rules': self.rules,
            })

    def broadcast(self, event_name=None, source_node_uuid=None, target_node_uuid=None, data=None):
        self.channel.basic_publish(
            exchange='',
            routing_key=f'broadcast-{self.origin_source_uuid}',
            body=json.dumps({
                'event_name': event_name,
                'source_node_uuid': source_node_uuid,
                'target_node_uuid': target_node_uuid,
                'origin_source_url': self.origin_source_url,
                'data': data,
            }, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def publish_child(self, body):
        self.channel.basic_publish(
            exchange='',
            routing_key=f'fetch-{self.origin_source_uuid}',
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
