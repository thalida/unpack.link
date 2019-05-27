import re
from pprint import pprint
from ...helpers import UnpackHelpers

class TypeBase():
    NAME = 'base'
    URL_PATTERN = re.compile(r'.*', re.IGNORECASE)
    NODE_TYPE = 'url'

    @classmethod
    def setup_node(cls, node_url, node_data=None, branch_nodes=[], is_error=False, is_from_db=False):
        node = {
            'type': cls.NODE_TYPE,
            'url': node_url,
            'data': node_data,
            'num_branches': len(branch_nodes),
            'is_from_db': is_from_db,
            'is_error': is_error,
        }

        return node

    @classmethod
    def fetch(cls, node_uuid, node_url, url_matches=None):
        # TODO: 25 MARCH 2019 [TNOEL]
        # Add in fetching using the two libraries below
        # Figure out how to spin off new jobs to request children
        # https://2.python-requests.org/en/master/
        # https://github.com/scrapy/parsel

        is_from_db = True
        raw_node, raw_branch_nodes = cls.get_node_and_branches_from_db(node_uuid, node_url)

        if raw_node is None:
            is_from_db = False
            raw_node, raw_branch_nodes = cls.get_node_and_branches_from_web(node_uuid, node_url, url_matches=url_matches)

        node = cls.setup_node(
            node_url=node_url,
            node_data=raw_node.get('data'),
            branch_nodes=raw_branch_nodes,
            is_error=raw_node.get('is_error', False),
            is_from_db=is_from_db,
        )

        return node, raw_branch_nodes

    @classmethod
    def get_node_and_branches_from_db(cls, node_uuid, node_url):
        raw_node = UnpackHelpers.fetch_node_by_uuid(node_uuid)
        raw_branches = []

        if raw_node is not None:
            raw_branches = UnpackHelpers.fetch_node_children(node_uuid)

        return raw_node, raw_branches

    @classmethod
    def get_node_and_branches_from_web(cls, node_uuid, node_url, url_matches=None):
        return {'data': {'uuid': node_uuid, 'url': node_url, 'url_matches': url_matches}}, []
