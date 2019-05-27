from pprint import pprint
import json

from flask_socketio import SocketIO
from redis import Redis
from rq import Queue

from app import hash_url
from .helpers import UnpackHelpers
from .types.base import TypeBase
from .types.media import TypeMedia
from .types.twitter import TypeTwitter

redis_conn = Redis()
unpackers_q = Queue("unpackers", connection=redis_conn)
controllers_q = Queue("controllers", connection=redis_conn)
socketio = SocketIO(message_queue='redis://')

# thread_example = 1048986902098059267
# quoted_example = 1048977169186271232
# multi_quote_example = 1048991778119008258
# simple_weird_tree = 1048989029486809088
# medium_weird_tree = 1049037454710394881
# large_weird_tree = 946823401217380358
# deleted_quoted_tweet = 946795191784132610

class Unpack:
    NODE_TYPES = [
        TypeTwitter(),
        TypeMedia(),

        # TypeBase should always be last
        TypeBase(),
    ]

    def __init__(self, node_url=None, node_uuid=None, parent_node_uuid=None):
        self.unpack_job_id = None
        self.request_job_id = None

        if node_uuid is None:
            node_uuid = UnpackHelpers.fetch_node_uuid_by_url(node_url)

        if node_url is None:
            node_url = UnpackHelpers.fetch_node_url_by_uuid(node_uuid)

        self.node_uuid = node_uuid
        self.node_url = node_url
        self.node_url_hash = hash_url(node_url)
        self.parent_node_uuid = parent_node_uuid
        self.is_parent_node = self.parent_node_uuid is None

        self.EVENT_KEYS = {
            'TREE_INIT': f'tree_init:{self.node_url_hash}',
            'TREE_UPDATE': f'tree_update:{self.node_url_hash}',
        }

        if self.is_parent_node:
            self.handle_controller()

        self.handle_unpack()


    def handle_controller(self):
        request_job = UnpackHelpers.find_job_by_node_uuid(controllers_q.jobs, self.node_uuid)
        if request_job is None:
            request_job = controllers_q.enqueue(self.start_coordinator)
            request_job.meta['node_uuid'] = self.node_uuid
            request_job.save_meta()

        self.request_job_id = request_job.id


    def handle_unpack(self):
        unpack_job = UnpackHelpers.find_job_by_node_uuid(unpackers_q.jobs, self.node_uuid)
        if unpack_job is None:
            unpack_job = unpackers_q.enqueue(self.walk_node_tree)
            unpack_job.meta['node_uuid'] = self.node_uuid
            unpack_job.save_meta()

        self.unpack_job_id = unpack_job.id


    def walk_node_tree(self):
        type_cls, node_url_match = Unpack.get_node_type_class_by_url(self.node_url)
        node, branch_nodes = type_cls.fetch(self.node_uuid, self.node_url, url_matches=node_url_match)

        if node.get('is_from_db', False):
            return

        UnpackHelpers.store_node(self.node_uuid, node)

        if node['num_branches'] == 0:
            UnpackHelpers.store_relationship(self.node_uuid, None)
            return

        for branch in branch_nodes:
            branch['node_uuid'] = UnpackHelpers.fetch_node_uuid_by_url(branch.get('node_url'))
            UnpackHelpers.store_relationship(self.node_uuid, branch)
            Unpack(
                parent_node_uuid=self.node_uuid,
                node_uuid=branch.get('node_uuid', None),
                node_url=branch.get('node_url', None),
            )


    def start_coordinator(self):
        while True:
            tree = UnpackHelpers.get_node_descendants(self.node_uuid)
            parents = {branch.get('parent_node_uuid') for branch in tree}
            children = {branch.get('node_uuid') for branch in tree}
            children_without_children = children - parents
            has_only_terminal_nodes = len(children_without_children) == 1 and UnpackHelpers.TERMINAL_NODE_UUID in children_without_children

            if has_only_terminal_nodes:
                socketio.emit(self.EVENT_KEYS['TREE_UPDATE'], json.dumps(tree, default=str))
                break

    @staticmethod
    def get_node_type_class_by_url(node_url):
        for url_type in Unpack.NODE_TYPES:
            matches = url_type.URL_PATTERN.findall(node_url)
            if len(matches) > 0:
                type_cls = url_type
                node_match = matches[0]
                break

        return type_cls, node_match
