from pprint import pprint

from flask_socketio import SocketIO
from redis import Redis
from rq import Queue

from app import hash_url
from .helpers import UnpackHelpers

redis_conn = Redis()
q = Queue(connection=redis_conn)
socketio = SocketIO(message_queue='redis://')

# thread_example = 1048986902098059267
# quoted_example = 1048977169186271232
# multi_quote_example = 1048991778119008258
# simple_weird_tree = 1048989029486809088
# medium_weird_tree = 1049037454710394881
# large_weird_tree = 946823401217380358
# deleted_quoted_tweet = 946795191784132610

class Unpack:
    tree = None
    job = None

    def __init__(self, url):
        self.url = url
        self.url_hash = hash_url(self.url)
        self.EVENT_KEYS = {
            'TREE_INIT': f'tree_init:{self.url_hash}',
            'TREE_UPDATE': f'tree_update:{self.url_hash}',
        }
        self.start_job()

    def start_job(self):
        found_job = UnpackHelpers.find_job_by_hash(q.jobs, self.url_hash)
        if found_job is not None:
            self.job = found_job
        else:
            self.job = q.enqueue(self.run)
            self.job.meta['url_hash'] = self.url_hash
            self.job.save_meta()

        return self.job

    def run(self):
        self.tree = UnpackHelpers.get_tree(url=self.url, url_hash=self.url_hash)
        self.broadcast(self.tree)

    def broadcast(self, tree):
        socketio.emit(self.EVENT_KEYS['TREE_UPDATE'], tree)
