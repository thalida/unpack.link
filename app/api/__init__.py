import logging
from pprint import pprint

from flask import Blueprint, make_response, jsonify, abort

from ..unpack import Unpack

logger = logging.getLogger(__name__)
api = Blueprint(
    'api',
    __name__,
    template_folder='../views',
    static_folder='../views'
)

@api.route('/api/tree/<path:url>', methods=['GET'])
def get_trees_by_path(url):
    try:
        unpacked = Unpack(url)
        return jsonify(unpacked.tree)
    except Exception:
        logger.exception('500 Error Fetching Window Outside')
        abort(500)

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
