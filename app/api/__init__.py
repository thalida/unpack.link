import logging
from pprint import pprint

from flask import Blueprint, make_response, jsonify, abort
from redis import Redis
from rq import Queue

from ..unpack import Unpack

logger = logging.getLogger(__name__)
api = Blueprint(
    'api',
    __name__,
    template_folder='../views',
    static_folder='../views'
)

redis_conn = Redis()
q = Queue(connection=redis_conn)

@api.route('/api/tree/<path:url>', methods=['GET'])
def get_trees_by_path(url):
    try:
        unpack = Unpack()
        job = q.enqueue(unpack.run, url)
        return jsonify({'job': job.id})
    except Exception:
        logger.exception('500 Error With /api/tree')
        abort(500)

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
