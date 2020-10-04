import log
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
            import api
            api.main()
        except Exception:
            logger.exception('Error importing and running api')

    elif args.action == 'queue-manager':
        try:
            import queues.manager
            queues.manager.main(request_id=args.request)
        except Exception:
            logger.exception('Error importing and running queues.manager')

    elif args.action == 'queue-fetcher-worker':
        try:
            import queues.consumers.fetcher
            queues.consumers.fetcher.main(request_id=args.request)
        except Exception:
            logger.exception('Error importing and running queues.consumers.fetcher')

    elif args.action == 'queue-broadcast-worker':
        try:
            import queues.consumers.broadcaster
            queues.consumers.broadcaster.main(request_id=args.request)
        except Exception:
            logger.exception('Error importing and running queues.consumers.broadcaster')

if __name__ == '__main__':
    main()
