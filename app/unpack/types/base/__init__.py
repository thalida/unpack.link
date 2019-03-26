import re
from pprint import pprint

from app import hash_url

class TypeBase():
    NAME = 'base'
    URL_PATTERN = re.compile(r'.*', re.IGNORECASE)

    @staticmethod
    def setup_node(url, data=None, branches=list(), num_branches=0, node_type=None, relationship=None, error=None, is_error=False, is_from_db=False):
        node = {
            'url': url,
            'url_hash': hash_url(url),
            'type': node_type,
            'data': data,
            'relationship': relationship,
            'branches': branches.copy(),
            'num_branches': num_branches,
            'is_error': is_error,
            'is_from_db': is_from_db,
        }

        if error is not None:
            node['is_error'] = True
            node['data'] = str(error)

        return node

    def fetch(self, url, relationship=None):
        node = self.setup_node(url, data={'url': url}, node_type='url', relationship=relationship)
        branches = []
        # MAYBE: google image search?
        return node, branches
