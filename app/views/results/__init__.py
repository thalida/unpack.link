from pprint import pprint
import json
import logging

from flask import Blueprint, request, abort, render_template

from ...unpack.helpers import UnpackHelpers

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
        return render_template('results/index.html')
    except Exception:
        logger.exception('Error loading results view')
        abort(500)
