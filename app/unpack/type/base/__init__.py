import re
from pprint import pprint

class TypeBase():
    NAME = 'base'
    URL_PATTERN = re.compile(r'.*', re.IGNORECASE)

    def setup_node(self, data=None, branches=[], num_branches=0, node_type=None, relationship=None, error=None):
        node = {
            'type': node_type,
            'data': data,
            'relationship': relationship,
            'branches': branches.copy(),
            'num_branches': num_branches,
            'has_error': False,
        }

        if error is not None:
            node['has_error'] = True
            node['error'] = str(error)

        return node

    def fetch(self, url, relationship=None):
        node = self.setup_node(data={'url': url}, node_type='url', relationship=relationship)
        branches = []
        # MAYBE: google image search?
        return node, branches
