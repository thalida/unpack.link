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
    def get_tree(url=None, url_hash=None, tree=None, parent_node_hash=None, relationship=None):
        if (url is None or url_hash is None) and (url is not None or url_hash is not None):
            if url_hash is None:
                url_hash = hash_url(url)
            else:
                url = UnpackHelpers.fetch_url_by_hash(url_hash)

        if url_hash is None and url is None:
            raise Exception('get_tree requires url or url_hash')

        if tree is None:
            tree = {'branches': []}

        node, raw_branches = UnpackHelpers.get_node_from_db(url_hash, relationship=relationship)
        if node is None:
            node, raw_branches = UnpackHelpers.get_node_from_web(url, relationship=relationship)
            UnpackHelpers.store_node_and_branch(node, parent_node_hash=parent_node_hash)

        for branch in raw_branches:
            node = UnpackHelpers.get_tree(
                url=branch.get('url', None),
                url_hash=branch.get('child_url_hash', None),
                tree=node,
                parent_node_hash=node['url_hash'],
                relationship=branch['relationship']
            )

        tree['branches'].append(node)
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
    def store_node_and_branch(node_obj, parent_node_hash=None):
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

            if parent_node_hash is not None:
                branch_query = """
                        INSERT INTO branch (parent_url_hash, child_url_hash, relationship)
                        VALUES (%s, %s, %s)
                        RETURNING *
                        """
                branch_data = (parent_node_hash, node_obj['url_hash'], node_obj['relationship'])
                branch = UnpackHelpers.execute_sql('fetchone', branch_query, branch_data)

            return node
        except Exception:
            UnpackHelpers.raise_error('Error inserting a new node: {node}', node=node_obj)

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
                FROM branch as br
                WHERE parent_url_hash = %s
                AND created_on >= (
                    SELECT max(n.created_on)
                    FROM node as n
                    WHERE n.url_hash = %s
                )
                ORDER BY br.created_on DESC
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
