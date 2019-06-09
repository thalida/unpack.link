"""controller.py

[description]

Attributes
==========
os.environ['TZ'] : UTC
    Force server to use UTC time
args : 'web-server', 'broadcaster', 'fetcher'
    Available actions to trigger
"""

import os
os.environ['TZ'] = 'UTC'

import argparse

def main():
    parser = argparse.ArgumentParser(description='Start an unpack queue...')
    parser.add_argument('action',
                        choices=['web-server', 'broadcaster', 'fetcher'],
                        help='Unpack queue name')
    args = parser.parse_args()

    if args.action == 'web-server':
        import app.web_server
        app.web_server.main()

    elif args.action == 'broadcaster':
        import unpack.broadcaster
        unpack.broadcaster.main()

    elif args.action == 'fetcher':
        import unpack.fetcher
        unpack.fetcher.main()

if __name__ == '__main__':
    main()
