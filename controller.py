"""controller.py

[description]

Attributes
==========
os.environ['TZ'] : UTC
    Force server to use UTC time
args : 'api-server', 'broadcaster', 'fetcher'
    Available actions to trigger
"""

import os
os.environ['TZ'] = 'UTC'

import argparse

def main():
    parser = argparse.ArgumentParser(description='Start an unpack queue...')
    parser.add_argument('action',
                        choices=['api-server', 'broadcaster', 'fetcher-p0', 'fetcher-p1'],
                        help='Unpack queue name')
    args = parser.parse_args()

    if args.action == 'api-server':
        import unpack.api.server
        unpack.api.server.main()

    elif args.action == 'broadcaster':
        import unpack.queues.broadcaster.consumer
        unpack.queues.broadcaster.consumer.main()

    elif args.action == 'fetcher-p0':
        import unpack.queues.fetcher.consumer_p0
        unpack.queues.fetcher.consumer_p0.main()

    elif args.action == 'fetcher-p1':
        import unpack.queues.fetcher.consumer_p1
        unpack.queues.fetcher.consumer_p1.main()

if __name__ == '__main__':
    main()
