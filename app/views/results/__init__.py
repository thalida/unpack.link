import logging
from pprint import pprint

from flask import Blueprint, request, abort, render_template

from ...unpack import Unpack

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
        unpacked = Unpack(url)
        return render_template(
            'results/index.html',
            page_context={
                'EVENT_KEYS': {**unpacked.EVENT_KEYS},
                'URL_HASH': unpacked.url_hash,
                'JOB_ID': unpacked.job.id
            }
        )
    except Exception:
        logger.exception('Error loading results view')
        abort(500)
