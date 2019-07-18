import sys
import traceback
import os
os.environ['TZ'] = 'UTC'

import argparse

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pika").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("ampq").setLevel(logging.WARNING)

root_logger = logging.getLogger()

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('/tmp/unpack_logs.log')

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
root_logger.addHandler(c_handler)
root_logger.addHandler(f_handler)

logger = logging.getLogger(__name__)


def handle_excepthook(exctype, value, tb):
    uncaught_logger = logging.getLogger('uncaught')
    message = ''.join(traceback.format_exception(exctype, value, tb))
    uncaught_logger.critical(message)

sys.excepthook = handle_excepthook


def main():
    parser = argparse.ArgumentParser(description='Start an unpack queue...')
    parser.add_argument(
        'action',
        choices=[
            'api',
            'queue-manager',
            'queue-fetcher-worker',
            'queue-broadcast-worker',
        ],
        help='Unpack action'
    )
    parser.add_argument('-q', '--request', help="Request Id")

    args = parser.parse_args()

    if args.action == 'api':
        import unpack.api
        unpack.api.main()

    elif args.action == 'queue-manager':
        import unpack.queues.manager
        unpack.queues.manager.main(request_id=args.request)

    elif args.action == 'queue-fetcher-worker':
        import unpack.queues.consumers.fetcher
        unpack.queues.consumers.fetcher.main(request_id=args.request)

    elif args.action == 'queue-broadcast-worker':
        import unpack.queues.consumers.broadcaster
        unpack.queues.consumers.broadcaster.main(request_id=args.request)

if __name__ == '__main__':
    main()
