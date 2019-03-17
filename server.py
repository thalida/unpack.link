import os
os.environ['TZ'] = 'UTC'

import logging
from pprint import pprint
from flask import Flask, abort

from app.api import api
from app.views import input_view, results_view

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder = './app/views')
app.url_map.strict_slashes = False

blueprints = [api, input_view, results_view]
for bp in blueprints:
    app.register_blueprint(bp)

@app.errorhandler(404)
def not_found(error):
    return abort(404)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5001')
    # socketio.run(app, debug=True, host='0.0.0.0', port='5002')


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
