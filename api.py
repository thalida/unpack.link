# !!!!!
import os
os.environ['TZ'] = 'UTC'

import logging
from pprint import pprint
from flask import Flask, request, make_response, jsonify, abort

from modules.unpack import Unpack

logger = logging.getLogger(__name__)
api = Flask(__name__)


thread_example = 1048986902098059267
quoted_example = 1048977169186271232
multi_quote_example = 1048991778119008258
simple_weird_tree = 1048989029486809088
medium_weird_tree = 1049037454710394881
large_weird_tree = 946823401217380358
deleted_quoted_tweet = 946795191784132610

# example_status_id = thread_example
# example_status_id = quoted_example
# example_status_id = multi_quote_example
# example_status_id = simple_weird_tree
# example_status_id = medium_weird_tree
# example_status_id = large_weird_tree
# example_status_id = deleted_quoted_tweet
# example_url = f'https://twitter.com/i/web/status/{example_status_id}'

@api.route('/api/v1/tree/<int:tree_id>', methods=['GET'])
def get_trees_by_id(tree_id):
    try:
        unpack = Unpack(tree_id)
        return jsonify(unpack.tree)
    except Exception:
        logger.exception('500 Error Fetching Window Outside')
        abort(500)

@api.route('/api/v1/tree/path/<path:path>', methods=['GET'])
def get_trees_by_path(path):
    try:
        unpack = Unpack(None, path=path)
        return jsonify(unpack.tree)
    except Exception:
        logger.exception('500 Error Fetching Window Outside')
        abort(500)

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    api.run(debug=True, host='0.0.0.0', port='5001')
