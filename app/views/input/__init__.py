import logging
from pprint import pprint

from flask import Blueprint, abort, render_template

logger = logging.getLogger(__name__)
input_view = Blueprint(
    'input_view',
    __name__,
    template_folder='../',
    static_folder='../'
)

@input_view.route('/', methods=['GET'])
@input_view.route('/input', methods=['GET'])
def view():
    try:
        return render_template(
            'input/index.html',
            page_context={})
    except Exception:
        logger.exception('Error loading input view')
        abort(500)
