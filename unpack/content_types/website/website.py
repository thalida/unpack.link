import log
import os
os.environ['TZ'] = 'UTC'

import logging
logger = logging.getLogger(__name__)

import re
import json
import datetime
import urllib.robotparser
from urllib.parse import urlparse, urljoin
import requests
from parsel import Selector

from helpers import UnpackHelpers
from exceptions import CannotFetchNode


class ContentTypeWebsite:
    TYPE = 'website'
    URL_PATTERN = re.compile(r'.*', re.IGNORECASE)
    USER_AGENT_PART = ''
    DEFAULT_RULES = {
        'force_from_web': False,
        'force_from_db': False,
        'refresh_after': 1 * 86400,  # 1 day
    }

    @classmethod
    def get_user_agent(cls):
        bot_type = ''

        if len(cls.USER_AGENT_PART) > 0:
            bot_type = f'-{cls.USER_AGENT_PART}'

        return f'{UnpackHelpers.USER_AGENT}{bot_type}'

    @classmethod
    def get_headers(cls):
        bot_type = ''

        if len(cls.USER_AGENT_PART) > 0:
            bot_type = f'-{cls.USER_AGENT_PART}'

        return {
            'User-Agent': cls.get_user_agent()
        }

    @classmethod
    def get_can_fetch(cls, node_url):
        user_agent = cls.get_user_agent()
        parsed_url = urlparse(node_url)
        robot_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        robotparser = urllib.robotparser.RobotFileParser()
        robotparser.set_url(robot_url)
        robotparser.read()
        return robotparser.can_fetch(user_agent, node_url)

    @classmethod
    def setup_node_details(cls, node_data=None, is_error=False, is_from_db=False, error_type=None):
        node_details = {
            'node_type': cls.TYPE,
            'data': node_data,
            'is_error': is_error,
            'is_from_db': is_from_db,
        }

        if is_error:
            node_details['error_type'] = error_type

        return node_details

    @classmethod
    def fetch(cls, node_uuid, node_url, url_matches=None, rules=None):
        rules = {**cls.DEFAULT_RULES, **rules}

        if rules['force_from_db']:
            is_from_db = True
            raw_node_details, raw_links = cls.get_node_and_links_from_db(node_uuid)
        elif rules['force_from_web']:
            is_from_db = False
            raw_node_details, raw_links = cls.get_node_and_links_from_web(
                node_url,
                url_matches=url_matches
            )
        else:
            now = datetime.datetime.now()
            min_update_date = now - datetime.timedelta(seconds=rules['refresh_after'])
            is_from_db = True
            raw_node_details, raw_links = cls.get_node_and_links_from_db(node_uuid, min_update_date=min_update_date)

            if raw_node_details is None:
                is_from_db = False
                raw_node_details, raw_links = cls.get_node_and_links_from_web(
                    node_url,
                    url_matches=url_matches
                )

        node_details = cls.setup_node_details(
            node_data=raw_node_details.get('data'),
            is_error=raw_node_details.get('is_error', False),
            error_type=raw_node_details.get('error_type'),
            is_from_db=is_from_db,
        )

        return node_details, raw_links

    @classmethod
    def get_node_and_links_from_db(cls, node_uuid, min_update_date=None):
        raw_node_details = UnpackHelpers.fetch_node(node_uuid, min_update_date=min_update_date)
        raw_links = []

        if raw_node_details is not None:
            raw_links = UnpackHelpers.fetch_links_by_source(node_uuid)

        return raw_node_details, raw_links

    @classmethod
    def get_node_and_links_from_web(cls, node_url, url_matches=None):
        try:
            if not cls.get_can_fetch(node_url):
                raise CannotFetchNode(node_url)

            headers = cls.get_headers()
            timeout = (2, 5)
            page_source = requests.get(node_url, timeout=timeout, headers=headers).text

        except Exception as e:
            node_details = cls.setup_node_details(
                error_type=type(e).__name__,
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
                    'favicon': None,
                }
            }

            shortcut_favicon = sel.css('link[rel*=shortcut]::attr(href)').get()
            icon_favicon = sel.css('link[rel*=icon]::attr(href)').get()

            if shortcut_favicon and len(shortcut_favicon) > 0:
                node_data['meta']['favicon'] = urljoin(node_url, shortcut_favicon)
            elif icon_favicon and len(icon_favicon) > 0:
                node_data['meta']['favicon'] = urljoin(node_url, icon_favicon)

            node_details = cls.setup_node_details(node_data=node_data)
            raw_links = []

            link_elements = sel.css('body a, body img')
            for idx, el in enumerate(link_elements):
                link_href = el.attrib.get('href', None)
                link_src = el.attrib.get('src', None)

                if link_href is None and link_src is None:
                    continue

                rel = el.attrib.get('rel', '')
                nofollow = rel.find('nofollow') != -1

                if nofollow:
                    logger.debug([link_href, link_src])

                link = None
                link_type = None
                if link_href is not None:
                    link = link_href
                    link_type = 'link'
                else:
                    link = link_src
                    link_type = 'media'

                raw_links.append({
                    'target_node_url': urljoin(node_url, link),
                    'link_type': link_type,
                    'weight': idx,
                    'nofollow': nofollow
                })

        return node_details, raw_links
