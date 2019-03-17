import logging
from pprint import pprint

import hashlib

from flask import Blueprint, request, abort, render_template
from redis import Redis
from rq import Queue

from ...unpack import Unpack

redis_conn = Redis()
q = Queue(connection=redis_conn)

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
        unpack = Unpack(url)
        job = q.enqueue(unpack.run)
        print(unpack.EVENT_KEYS)
        return render_template(
            'results/index.html',
            page_context={
                'EVENT_KEYS': {**unpack.EVENT_KEYS},
                'URL_HASH': unpack.url_hash,
                'JOB_ID': job.id
            }
        )
    except Exception:
        logger.exception('Error loading results view')
        abort(500)
