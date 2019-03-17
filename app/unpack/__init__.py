from pprint import pprint

import hashlib

from flask_socketio import SocketIO
from redis import Redis
from rq import Queue

from .type.base import TypeBase
from .type.media import TypeMedia
from .type.twitter import TypeTwitter

redis_conn = Redis()
q = Queue(connection=redis_conn)
socketio = SocketIO(message_queue='redis://')

# thread_example = 1048986902098059267
# quoted_example = 1048977169186271232
# multi_quote_example = 1048991778119008258
# simple_weird_tree = 1048989029486809088
# medium_weird_tree = 1049037454710394881
# large_weird_tree = 946823401217380358
# deleted_quoted_tweet = 946795191784132610
# example_status_id = thread_example
# example_status_id = quoted_example
# example_status_id = multi_quote_example
# example_status_id = simple_weird_tree
# example_status_id = medium_weird_tree
# example_status_id = large_weird_tree
# example_status_id = deleted_quoted_tweet
# example_url = f'https://twitter.com/i/web/status/{example_status_id}'

# add reddit using their api
# add insta (check if they have one?)
# add any url (every single href on the page + the meta data)

class Unpack:
    def __init__(self, url):
        self.url_types = [
            TypeTwitter(),
            TypeMedia(),
            TypeBase(),
        ]
        self.tree = None
        self.url = url
        self.url_hash = hashlib.md5(str(self.url).encode('utf-8')).hexdigest();
        self.EVENT_KEYS = {
            'TREE_UPDATE': f'tree_update:{self.url_hash}',
        }
        self.job = q.enqueue(self.run)

    def run(self):
        self.tree = self.__fetch_tree(self.url)
        self.__broadcast()

    def __fetch_tree(self, branch, tree=None):
        if isinstance(branch, str):
            branch = {'url': branch}

        if tree is None:
            tree = {'branches': []}

        node_type_cls = None
        node_id = None

        for url_type in self.url_types:
            matches = url_type.URL_PATTERN.findall(branch['url'])
            if len(matches) > 0:
                node_type_cls = url_type
                node_id = matches[0]
                break

        node, next_branches = node_type_cls.fetch(node_id, relationship=branch.get('relationship', None))

        for next_br in next_branches:
            node = self.__fetch_tree(next_br, tree=node)

        tree['branches'].append(node)
        return tree

    def __broadcast(self):
        print(self.EVENT_KEYS['TREE_UPDATE'])
        socketio.emit(self.EVENT_KEYS['TREE_UPDATE'], self.tree)

