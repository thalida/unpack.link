import os
import json
import logging
from pprint import pprint
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

from app import ENV_VARS

logger = logging.getLogger(__name__)

class UnpackHelpers:
    DB_CREDS = {
        'host': os.getenv(ENV_VARS['DB']['HOST'], 'localhost'),
        'dbname': os.getenv(ENV_VARS['DB']['NAME']),
        'user': os.getenv(ENV_VARS['DB']['USER']),
        'password': os.getenv(ENV_VARS['DB']['PASSWORD'], None),
    }

    TERMINAL_NODE_UUID = str(uuid.UUID(int=0))

    @staticmethod
    def get_node_descendants(node_uuid):
        tree = []
        branches = UnpackHelpers.fetch_node_children(node_uuid)

        if branches is None or len(branches) == 0:
            return tree

        for branch in branches:
            tree.append(branch)
            tree = tree + UnpackHelpers.get_node_descendants(branch.get('node_uuid'))

        return tree


    @staticmethod
    def execute_sql(fetch_action, query, query_args):
        with psycopg2.connect(**UnpackHelpers.DB_CREDS) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, query_args)
                fetch_fn = getattr(cur, fetch_action)
                response = fetch_fn()

        return response

    @staticmethod
    def store_node(node_uuid, node_obj):
        try:
            node_query = """
                    INSERT INTO node (uuid, type, data, is_error)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """
            node_data = (
                node_uuid,
                node_obj['type'],
                json.dumps(node_obj['data']),
                node_obj['is_error']
            )
            node = UnpackHelpers.execute_sql('fetchone', node_query, node_data)
            return node
        except Exception:
            UnpackHelpers.raise_error('Error inserting a new node: {node}', node=node_obj)

    @staticmethod
    def store_relationship(parent_node_uuid, branch):
        try:
            branch = branch if branch is not None else {}
            query = """
                    INSERT INTO relationship (parent_node_uuid, node_uuid, relationship_score)
                    VALUES (%s, %s, %s)
                    RETURNING *
                    """
            branch_node_uuid = branch.get('node_uuid', UnpackHelpers.TERMINAL_NODE_UUID)
            relationship_score = branch.get('relationship_score', None)
            data = (parent_node_uuid, branch_node_uuid, relationship_score)
            return UnpackHelpers.execute_sql('fetchone', query, data)
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error inserting a branch: {branch}', branch=branch)

    @staticmethod
    def fetch_node_by_uuid(node_uuid):
        try:
            node = UnpackHelpers.execute_sql(
                'fetchone',
                """
                SELECT *
                FROM node
                WHERE uuid = %s
                """,
                (node_uuid,)
            )
            return node
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error fetching node with node_uuid: {node_uuid}', node_uuid=node_uuid)

    @staticmethod
    def fetch_node_children(parent_node_uuid):
        try:
            node = UnpackHelpers.execute_sql(
                'fetchall',
                """
                SELECT *
                FROM relationship as r
                WHERE parent_node_uuid = %s
                AND created_on >= (
                    SELECT max(n.created_on)
                    FROM node as n
                    WHERE n.uuid = %s
                )
                ORDER BY r.created_on DESC
                """,
                (parent_node_uuid,parent_node_uuid,)
            )
            return node
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error fetching children for: {parent_node_uuid}',
                            parent_node_uuid=parent_node_uuid)

    @staticmethod
    def fetch_node_uuid_by_url(node_url):
        try:
            node_uuid = UnpackHelpers.execute_sql(
                'fetchone',
                """
                SELECT node_uuid
                FROM url_uuid_map
                WHERE node_url = %s
                """,
                (node_url,)
            )

            if node_uuid is None:
                node_uuid = UnpackHelpers.execute_sql(
                    'fetchone',
                    """
                    INSERT INTO url_uuid_map (node_url)
                    VALUES (%s)
                    RETURNING node_uuid
                    """,
                    (node_url,)
                )
            return node_uuid.get('node_uuid')
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error fetching node uuid for url: {node_url}', node_url=node_url)

    @staticmethod
    def fetch_node_url_by_uuid(node_uuid):
        try:
            node_url = UnpackHelpers.execute_sql(
                'fetchone',
                """
                SELECT node_url
                FROM url_uuid_map
                WHERE node_uuid = %s
                """,
                (node_uuid,)
            )
            return node_url.get('node_url')
        except Exception:
            UnpackHelpers.raise_error('Unpack: Error fetching node url for uuid: {node_uuid}', node_uuid=node_uuid)

    @staticmethod
    def find_job_by_node_uuid(queued_jobs, node_uuid):
        found_job = None
        for job in queued_jobs:
            if job.meta.get('node_uuid') == node_uuid:
                found_job = job
                break;

        return found_job

    @staticmethod
    def raise_error(msg, **kwargs):
        msg = 'spomething bad happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
