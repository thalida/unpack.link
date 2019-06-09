import re
from pprint import pprint
import json
from urllib.parse import urljoin

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector

from ...helpers import UnpackHelpers

options = Options()
options.headless = True

class TypeBase:
    TYPE = 'base'
    URL_PATTERN = re.compile(r'.*', re.IGNORECASE)

    @classmethod
    def setup_node_details(cls, node_data=None, branch_nodes=[], is_error=False, is_from_db=False):
        node_details = {
            'node_type': cls.TYPE,
            'data': json.dumps(node_data, default=str),
            'branch_nodes': branch_nodes,
            'num_branches': len(branch_nodes),
            'is_error': is_error,
            'is_from_db': is_from_db,
        }

        return node_details

    @classmethod
    def fetch(cls, node_uuid, node_url, url_matches=None, force_update=True):
        is_from_db = True
        raw_node_details, raw_links = cls.get_node_and_links_from_db(node_uuid, node_url)

        if force_update or raw_node_details is None:
            is_from_db = False
            raw_node_details, raw_links = cls.get_node_and_links_from_web(node_url, url_matches=url_matches)

        node_details = cls.setup_node_details(
            node_data=raw_node_details.get('data'),
            branch_nodes=raw_links,
            is_error=raw_node_details.get('is_error', False),
            is_from_db=is_from_db,
        )

        return node_details, raw_links

    @classmethod
    def get_node_and_links_from_db(cls, node_uuid, node_url):
        raw_node_details = UnpackHelpers.fetch_node_metadata(node_uuid)
        raw_links = []

        if raw_node_details is not None:
            raw_links = UnpackHelpers.fetch_links_by_source(node_uuid)

        return raw_node_details, raw_links

    @classmethod
    def get_node_and_links_from_web(cls, node_url, url_matches=None):
        try:
            driver = webdriver.Chrome(ChromeDriverManager('2.42').install(), chrome_options=options)
            driver.get(node_url)
            page_source = driver.page_source
            driver.close()
        except selenium.common.exceptions.WebDriverException as e:
            node_details = cls.setup_node_details(node_data=str(e), is_error=True)
            raw_links = []
        except Exception as e:
            node_details = cls.setup_node_details(node_data=str(e), is_error=True)
            raw_links = []
        else:
            sel = Selector(text=page_source)

            node_data = {'url_matches': url_matches, 'page_source': page_source}
            node_details = cls.setup_node_details(node_data=node_data)

            page_links = set(sel.css('*::attr(href)').getall())
            abs_page_links = [urljoin(node_url, link) for link in page_links]
            raw_links = [{'target_node_url': link, 'link_type': 'link'} for link in abs_page_links]

        return node_details, raw_links
