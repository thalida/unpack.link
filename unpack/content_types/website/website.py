import re
import json
from urllib.parse import urljoin
import datetime

import requests
from parsel import Selector

from ...helpers import UnpackHelpers


class ContentTypeWebsite:
    TYPE = 'website'
    URL_PATTERN = re.compile(r'.*', re.IGNORECASE)

    DEFAULT_RULES = {
        'force_from_web': False,
        'force_from_db': False,
        'refresh_after': 1 * 86400,  # 1 day
    }

    @classmethod
    def setup_node_details(cls, node_data=None, is_error=False, is_from_db=False):
        node_details = {
            'node_type': cls.TYPE,
            'data': node_data,
            'is_error': is_error,
            'is_from_db': is_from_db,
        }

        return node_details

    @classmethod
    def fetch(cls, node_uuid, node_url, url_matches=None, rules=None):
        rules = {**cls.DEFAULT_RULES, **rules}

        if rules['force_from_db']:
            is_from_db = True
            raw_node_details, raw_links = cls.get_node_and_links_from_db(
                node_uuid,
                node_url
            )
        elif rules['force_from_web']:
            is_from_db = False
            raw_node_details, raw_links = cls.get_node_and_links_from_web(
                node_url,
                url_matches=url_matches
            )
        else:
            now = datetime.datetime.now()
            min_update_date = now - datetime.timedelta(seconds=rules['refresh_after'])
            raw_node_details = UnpackHelpers.fetch_node(
                node_uuid,
                min_update_date=min_update_date
            )

            if raw_node_details is None:
                is_from_db = False
                raw_node_details, raw_links = cls.get_node_and_links_from_web(
                    node_url,
                    url_matches=url_matches
                )
            else:
                is_from_db = True
                raw_links = UnpackHelpers.fetch_links_by_source(node_uuid)

        node_details = cls.setup_node_details(
            node_data=raw_node_details.get('data'),
            is_error=raw_node_details.get('is_error', False),
            is_from_db=is_from_db,
        )

        return node_details, raw_links

    @classmethod
    def get_node_and_links_from_db(cls, node_uuid, node_url):
        raw_node_details = UnpackHelpers.fetch_node(node_uuid)
        raw_links = []

        if raw_node_details is not None:
            raw_links = UnpackHelpers.fetch_links_by_source(node_uuid)

        return raw_node_details, raw_links

    @classmethod
    def get_node_and_links_from_web(cls, node_url, url_matches=None):
        try:
            page_source = requests.get(node_url, timeout=(2, 5)).text
        except Exception as e:
            node_details = cls.setup_node_details(
                node_data=str(e),
                is_error=True
            )
            raw_links = []
        else:
            sel = Selector(text=page_source)

            twitter_meta = [
                {
                    'name': n.css('::attr(name)').get(),
                    'content': n.css('::attr(content)').get()
                }
                for n in sel.css('meta[name*=twitter]')
            ]
            og_meta = [
                {
                    'name': n.css('::attr(name)').get(),
                    'content': n.css('::attr(content)').get()
                }
                for n in sel.css('meta[name*=og]')
            ]
            node_data = {
                'meta': {
                    'title': sel.css('title::text').get(),
                    'description': sel.css('meta[name=description]::attr(content)').get(),
                    'twitter': twitter_meta,
                    'og': og_meta,
                    'favicon': sel.css('link[rel*=shortcut]::attr(href)').get(),
                }
            }

            if node_data['meta']['favicon'] and len(node_data['meta']['favicon']) > 0:
                node_data['meta']['favicon'] = urljoin(node_url, node_data['meta']['favicon'])

            node_details = cls.setup_node_details(node_data=node_data)

            page_links = sel.css('body a::attr(href), body img::attr(src)').getall()
            raw_links = []
            for idx, link in enumerate(page_links):
                raw_links.append({
                    'target_node_url': urljoin(node_url, link),
                    'link_type': 'link',
                    'weight': idx
                })

        return node_details, raw_links