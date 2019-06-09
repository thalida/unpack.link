import os
os.environ['TZ'] = 'UTC'

import argparse
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
