import re
from pprint import pprint

from twython import Twython
import twython.exceptions

from ..base import TypeBase
from . import secrets

class TypeTwitter(TypeBase):
    NAME = 'twitter'
    # TODO FIND ALL THE TWITTER PATTERNS
    URL_PATTERN = re.compile(r'twitter\.com(?:.*?)status/(\d+)', re.IGNORECASE)

    def __init__(self):
        auth_twitter = Twython(secrets.APP_KEY, secrets.APP_SECRET, oauth_version=2)
        ACCESS_TOKEN = auth_twitter.obtain_access_token()
        self.twitter = Twython(secrets.APP_KEY, access_token=ACCESS_TOKEN)

    def fetch(self, status_id, relationship=None, debug=False):
        try:
            tweet = self.twitter.show_status(
                id=int(status_id),
                tweet_mode="extended"
            )

            if debug:
                pprint(tweet)

            node = self.setup_node(data=tweet, node_type='tweet', relationship=relationship)
            branches = []

            # Get tweet media
            media = tweet['entities']['media'] if tweet['entities'].get('media') else []
            for m in media:
                branches.append({
                    'url': m['media_url_https'],
                    'relationship': 'link'
                })

            # Get tweet external links
            urls = tweet['entities'].get('urls')
            num_urls = len(urls) if urls else 0
            if num_urls > 1 or (num_urls == 1 and not tweet['is_quote_status']):
                for u in urls:
                    branches.append({
                        'url': u['expanded_url'],
                        'relationship': 'link'
                    })

            # Get quoted tweet
            if tweet['is_quote_status']:
                quoted_status_id = self.__get_quoted_status_id(tweet)
                branches.append({
                    'url': self.__make_path(quoted_status_id),
                    'relationship': 'quoted'
                })

            if tweet['in_reply_to_status_id']:
                branches.append({
                    'url': self.__make_path(tweet['in_reply_to_status_id']),
                    'relationship': 'replied_to'
                })

        except twython.exceptions.TwythonError as e:
            node = self.setup_node(node_type='tweet', relationship=relationship, error=e)
            branches = []

        finally:
            node['num_branches'] = len(branches)
            node['has_branches'] = node['num_branches'] > 0
            return node, branches


    def __make_path(self, id):
        return f'https://twitter.com/i/web/status/{id}'

    def __get_quoted_status_id(self, tweet):
        tweet_id = tweet.get('quoted_status', {}).get('id')

        if tweet_id is None:
            tweet_id = tweet.get('quoted_status_id')

        return tweet_id

