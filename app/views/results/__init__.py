import logging
from pprint import pprint

from flask import Blueprint, request, abort, render_template

logger = logging.getLogger(__name__)
results_view = Blueprint(
    'results_view',
    __name__,
    template_folder='../',
    static_folder='../'
)

@results_view.route('/results', methods=['GET'])
def view():
    try:
        url = request.args.get('url')
        return render_template('results/index.html', url_hash=url)
    except Exception:
        logger.exception('Error loading results view')
        abort(500)
