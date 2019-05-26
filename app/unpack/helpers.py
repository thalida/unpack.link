import os
import json
import logging
from pprint import pprint

import psycopg2
from psycopg2.extras import RealDictCursor

from app import ENV_VARS, hash_url
from .types.base import TypeBase
from .types.media import TypeMedia
from .types.twitter import TypeTwitter

logger = logging.getLogger(__name__)

class UnpackHelpers:
    URL_TYPES = [
        TypeTwitter(),
        TypeMedia(),
        # TypeBase should always be last
        TypeBase(),
    ]

    DB_CREDS = {
        'host': os.getenv(ENV_VARS['DB']['HOST'], 'localhost'),
        'dbname': os.getenv(ENV_VARS['DB']['NAME']),
        'user': os.getenv(ENV_VARS['DB']['USER']),
        'password': os.getenv(ENV_VARS['DB']['PASSWORD'], None),
    }

    @staticmethod
    def get_tree(url_hash, tree=[]):
        branches = UnpackHelpers.fetch_branches_by_parent_hash(url_hash)
        if branches is None or len(branches) == 0:
            return tree

        tree = tree + branches
        for branch in branches:
            tree = tree + UnpackHelpers.get_tree(branch.get('url_hash'))
        return tree

    @staticmethod
    def get_node_from_db(url_hash, relationship=None):
        raw_node = UnpackHelpers.fetch_node_by_hash(url_hash)
        if raw_node is None:
            return None, []

        type_cls, node_id = UnpackHelpers.find_type_by_url(raw_node['url'])
        raw_branches = UnpackHelpers.fetch_branches_by_parent_hash(url_hash)

        node = type_cls.setup_node(
            raw_node['url'],
            data=raw_node['data'],
            node_type=raw_node['type'],
            num_branches=len(raw_branches),
            relationship=relationship,
            is_error=raw_node['is_error'],
            is_from_db=True
        )

        return node, raw_branches

    @staticmethod
    def get_node_from_web(url, relationship=None):
        type_cls, node_id = UnpackHelpers.find_type_by_url(url)
        node, raw_branches = type_cls.fetch(node_id, relationship=relationship)

        return node, raw_branches


    @staticmethod
    def execute_sql(fetch_action, query, query_args):
        with psycopg2.connect(**UnpackHelpers.DB_CREDS) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, query_args)
                fetch_fn = getattr(cur, fetch_action)
                response = fetch_fn()

        return response

    @staticmethod
    def store_node(node_obj, parent_node_hash=None):
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
            node = UnpackHelpers.execute_sql('fetchone', node_query, node_data)
            return node
        except Exception:
            UnpackHelpers.raise_error('Error inserting a new node: {node}', node=node_obj)

    @staticmethod
    def store_branches(parent_node_obj, branches):
        try:
            branch_query = """
                    INSERT INTO relationship (parent_url_hash, url_hash, relationship_score)
                    VALUES (%s, %s, %s)
                    RETURNING *
                    """
            if branches is None or len(branches) == 0:
                UnpackHelpers.execute_sql('fetchone', branch_query, (parent_node_obj['url_hash'],'-1',None))
            else:
                for branch in branches:
                    branch_url_hash = branch.get('url_hash', hash_url(branch.get('url', None)))
                    branch_data = (parent_node_obj['url_hash'], branch_url_hash, branch.get('relationship', None))
                    UnpackHelpers.execute_sql('fetchone', branch_query, branch_data)

        except Exception:
            UnpackHelpers.raise_error('Error inserting a branches: {branches}', branches=branches)

    @staticmethod
    def fetch_url_by_hash(url_hash):
        try:
            node = UnpackHelpers.execute_sql(
                'fetchone',
                """
                SELECT url
                FROM node
                WHERE url_hash = %s
                """,
                (url_hash,)
            )
            return node['url'] if node is not None else node
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error fetching url by url_hash: {url_hash}', url_hash=url_hash)

    @staticmethod
    def fetch_node_by_hash(url_hash):
        try:
            node = UnpackHelpers.execute_sql(
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
            UnpackHelpers.raise_error('Unpack: Error fetching node with url_hash: {url_hash}', url_hash=url_hash)

    @staticmethod
    def fetch_branches_by_parent_hash(parent_url_hash):
        try:
            node = UnpackHelpers.execute_sql(
                'fetchall',
                """
                SELECT *
                FROM relationship as r
                WHERE parent_url_hash = %s
                AND created_on >= (
                    SELECT max(n.created_on)
                    FROM node as n
                    WHERE n.url_hash = %s
                )
                ORDER BY r.created_on DESC
                """,
                (parent_url_hash,parent_url_hash,)
            )
            return node
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error fetching branches for: {parent_url_hash}',
                            parent_url_hash=parent_url_hash)

    @staticmethod
    def find_type_by_url(url):
        for url_type in UnpackHelpers.URL_TYPES:
            matches = url_type.URL_PATTERN.findall(url)
            if len(matches) > 0:
                type_cls = url_type
                node_match = matches[0]
                break

        return type_cls, node_match

    @staticmethod
    def find_job_by_hash(queued_jobs, url_hash):
        found_job = None
        for job in queued_jobs:
            if job.meta.get('url_hash') == url_hash:
                found_job = job
                break;

        return found_job

    @staticmethod
    def raise_error(msg, **kwargs):
        msg = 'spomething bad happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
