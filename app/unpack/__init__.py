from pprint import pprint
from flask import jsonify

from .type.base import TypeBase
from .type.media import TypeMedia
from .type.twitter import TypeTwitter

# add reddit using their api
# add insta (check if they have one?)
# add any url (every single href on the page + the meta data)

class Unpack:
    def __init__(self, url, return_type=None):
        self.url_types = [
            TypeTwitter(),
            TypeMedia(),
            TypeBase(),
        ]

        self.tree = self.__fetch_tree({'url': url, 'relationship': None})

    def __fetch_tree(self, branch, tree={'branches': []}):
        node_type_cls = None
        node_id = None

        for url_type in self.url_types:
            matches = url_type.URL_PATTERN.findall(branch['url'])
            if len(matches) > 0:
                node_type_cls = url_type
                node_id = matches[0]
                break

        node, next_branches = node_type_cls.fetch(node_id, relationship=branch['relationship'])

        for next_br in next_branches:
            node = self.__fetch_tree(next_br, tree=node)

        tree['branches'].append(node)
        return tree

