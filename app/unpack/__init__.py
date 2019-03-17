import os
from pprint import pprint
import logging
import json

from flask_socketio import SocketIO
from redis import Redis
from rq import Queue
import psycopg2
from psycopg2.extras import RealDictCursor

from app import ENV_VARS, hash_url
from .types.base import TypeBase
from .types.media import TypeMedia
from .types.twitter import TypeTwitter

logger = logging.getLogger(__name__)
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
        self.db = {
            'host': os.getenv(ENV_VARS['DB']['HOST'], 'localhost'),
            'dbname': os.getenv(ENV_VARS['DB']['NAME']),
            'user': os.getenv(ENV_VARS['DB']['USER']),
            'password': os.getenv(ENV_VARS['DB']['PASSWORD'], None),
        }
        self.url_types = [
            TypeTwitter(),
            TypeMedia(),
            TypeBase(),
        ]
        self.tree = None
        self.url = url
        self.url_hash = hash_url(self.url)
        self.EVENT_KEYS = {
            'TREE_UPDATE': f'tree_update:{self.url_hash}',
        }
        self.job = q.enqueue(self.run)

    def run(self):
        self.tree = self.get_tree()

        if not self.tree[0]['is_from_db']:
            self.__store_tree(self.tree)

        self.__broadcast()

    def get_tree(self):
        stored_parent_node = self.__load_node(self.url_hash)
        if stored_parent_node is not None:
            tree = self.__load_tree(self.url_hash)
        else:
            tree = self.__fetch_tree(self.url)

        tree = [tree['branches'][0]]

        return tree

    def __broadcast(self):
        print(self.EVENT_KEYS['TREE_UPDATE'])
        socketio.emit(self.EVENT_KEYS['TREE_UPDATE'], self.tree)

    def __execute(self, fetch_action, query, query_args):
        with psycopg2.connect(**self.db) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, query_args)
                fetch_fn = getattr(cur, fetch_action)
                response = fetch_fn()

        return response

    def __load_node(self, url_hash):
        try:
            node = self.__execute(
                'fetchone',
                """
                SELECT *
                FROM node
                WHERE url_hash = %s
                """,
                (url_hash,)
            )
            return node
        except Exception:
            self.raise_error('Unpack: Error fetching url: {url_hash}', url_hash=url_hash)

    def __load_branches(self, parent_url_hash):
        try:
            node = self.__execute(
                'fetchall',
                """
                SELECT *
                FROM branches
                WHERE parent_url_hash = %s
                """,
                (parent_url_hash,)
            )
            return node
        except Exception:
            self.raise_error('Unpack: Error fetching branches for: {parent_url_hash}',
                            parent_url_hash=parent_url_hash)
    def __load_tree(self, url_hash, tree=None, relationship=None):
        if tree is None:
            tree = {'branches': []}

        raw_node = self.__load_node(url_hash)

        if raw_node is None:
            return tree

        raw_branches = self.__load_branches(url_hash)
        node = TypeBase.setup_node(
            raw_node['url'],
            data=raw_node['data'],
            node_type=raw_node['type'],
            num_branches=len(raw_branches),
            relationship=relationship,
            is_error=raw_node['is_error'],
            is_from_db=True
        )

        for branch in raw_branches:
            node = self.__load_tree(branch['child_url_hash'], tree=node, relationship=branch['relationship'])

        tree['branches'].append(node)
        return tree


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

    def __store_tree(self, tree, parent_node=None):
        for node in tree:
            self.__create_node(node, parent_node=parent_node)
            self.__store_tree(node['branches'], parent_node=node)

    def __create_node(self, node_obj, parent_node=None):
        try:
            node_query = """
                    INSERT INTO node (url_hash, url, type, data, is_error)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    """
            node_data = (
                node_obj['url_hash'],
                node_obj['url'], node_obj['type'],
                json.dumps(node_obj['data']),
                node_obj['is_error'],
            )
            node = self.__execute('fetchone', node_query, node_data)

            if parent_node is not None:
                branch_query = """
                        INSERT INTO branches (parent_url_hash, child_url_hash, relationship)
                        VALUES (%s, %s, %s)
                        RETURNING *
                        """
                branch_data = (parent_node['url_hash'], node_obj['url_hash'], node_obj['relationship'])
                branch = self.__execute('fetchone', branch_query, branch_data)

            return node
        except Exception:
            self.raise_error('Error inserting a new node: {node}', node=node_obj)

    @staticmethod
    def raise_error(msg, **kwargs):
        msg = 'spomething bad happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)

