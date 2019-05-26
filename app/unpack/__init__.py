from pprint import pprint
import json

from flask_socketio import SocketIO
from redis import Redis
from rq import Queue

from app import hash_url
from .helpers import UnpackHelpers

redis_conn = Redis()
unpackers_q = Queue("unpacks", connection=redis_conn)
requester_q = Queue("requests", connection=redis_conn)
socketio = SocketIO(message_queue='redis://')

# thread_example = 1048986902098059267
# quoted_example = 1048977169186271232
# multi_quote_example = 1048991778119008258
# simple_weird_tree = 1048989029486809088
# medium_weird_tree = 1049037454710394881
# large_weird_tree = 946823401217380358
# deleted_quoted_tweet = 946795191784132610

class Unpack:
    def __init__(self, url=None, url_hash=None, parent_node_hash=None, relationship=None):
        if (url is None or url_hash is None) and (url is not None or url_hash is not None):
            if url_hash is None:
                url_hash = hash_url(url)
            else:
                url = UnpackHelpers.fetch_url_by_hash(url_hash)

        if url_hash is None and url is None:
            raise Exception('get_tree requires url or url_hash')

        self.unpack_job_id = None
        self.request_job_id = None
        self.url = url
        self.url_hash = url_hash
        self.parent_node_hash = parent_node_hash
        self.is_parent_node = parent_node_hash is None

        # TODO: Change with new relationship math?
        self.relationship = relationship

        self.EVENT_KEYS = {
            'TREE_INIT': f'tree_init:{self.url_hash}',
            'TREE_UPDATE': f'tree_update:{self.url_hash}',
        }

        if self.is_parent_node:
            self.handle_request()

        self.handle_unpack()


    def handle_unpack(self):
        unpack_job = UnpackHelpers.find_job_by_hash(unpackers_q.jobs, self.url_hash)
        if unpack_job is None:
            unpack_job = unpackers_q.enqueue(self.get_tree)
            unpack_job.meta['url_hash'] = self.url_hash
            unpack_job.save_meta()

        self.unpack_job_id = unpack_job.id


    def handle_request(self):
        request_job = UnpackHelpers.find_job_by_hash(requester_q.jobs, self.url_hash)
        if request_job is None:
            request_job = requester_q.enqueue(self.start_coordinator)
            request_job.meta['url_hash'] = self.url_hash
            request_job.save_meta()

        self.request_job_id = request_job.id


    def get_tree(self):
        node, raw_branches = UnpackHelpers.get_node_from_db(self.url_hash, relationship=self.relationship)
        if node is None:
            node, raw_branches = UnpackHelpers.get_node_from_web(self.url, relationship=self.relationship)
            UnpackHelpers.store_node(node)
            UnpackHelpers.store_branches(node, raw_branches)

        for branch in raw_branches:
            if branch.get('url_hash') == '-1':
                continue;

            Unpack(
                parent_node_hash=node['url_hash'],
                url=branch.get('url', None),
                url_hash=branch.get('url_hash', None),
                relationship=branch.get('relationship', None),
            )


    def start_coordinator(self):
        while True:
            tree = UnpackHelpers.get_tree(self.url_hash)
            parents = {branch.get('parent_url_hash') for branch in tree}
            children = {branch.get('url_hash') for branch in tree}
            children_without_links = children - parents
            only_ends = len(children_without_links) == 1 and '-1' in children_without_links

            if only_ends:
                socketio.emit(self.EVENT_KEYS['TREE_UPDATE'], json.dumps(tree, default=str))
                break
