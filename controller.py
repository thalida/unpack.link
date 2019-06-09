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
                        choices=['api-server', 'broadcaster', 'fetcher'],
                        help='Unpack queue name')
    args = parser.parse_args()

    if args.action == 'api-server':
        import unpack.api.server
        unpack.api.server.main()

    elif args.action == 'broadcaster':
        import unpack.queues.broadcaster
        unpack.queues.broadcaster.main()

    elif args.action == 'fetcher':
        import unpack.queues.fetcher
        unpack.queues.fetcher.main()

if __name__ == '__main__':
    main()
