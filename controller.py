import unpack.log
import logging

import sys
import traceback
import os
os.environ['TZ'] = 'UTC'

import argparse

logger = logging.getLogger(__name__)


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
        try:
            import unpack.api
            unpack.api.main()
        except Exception:
            logger.exception('Error importing and running unpack.api')

    elif args.action == 'queue-manager':
        try:
            import unpack.queues.manager
            unpack.queues.manager.main(request_id=args.request)
        except Exception:
            logger.exception('Error importing and running unpack.queues.manager')

    elif args.action == 'queue-fetcher-worker':
        try:
            import unpack.queues.consumers.fetcher
            unpack.queues.consumers.fetcher.main(request_id=args.request)
        except Exception:
            logger.exception('Error importing and running unpack.queues.consumers.fetcher')

    elif args.action == 'queue-broadcast-worker':
        try:
            import unpack.queues.consumers.broadcaster
            unpack.queues.consumers.broadcaster.main(request_id=args.request)
        except Exception:
            logger.exception('Error importing and running unpack.queues.consumers.broadcaster')

if __name__ == '__main__':
    main()
