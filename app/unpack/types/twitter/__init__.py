import re
from pprint import pprint

from twython import Twython
import twython.exceptions

from ..base import TypeBase
from . import secrets

class TypeTwitter(TypeBase):
    NAME = 'twitter'
    NODE_TYPE = 'twitter'
    # TODO FIND ALL THE TWITTER PATTERNS
    URL_PATTERN = re.compile(r'twitter\.com(?:.*?)status/(\d+)', re.IGNORECASE)

    auth_twitter = Twython(secrets.APP_KEY, secrets.APP_SECRET, oauth_version=2)
    ACCESS_TOKEN = auth_twitter.obtain_access_token()
    twitter = Twython(secrets.APP_KEY, access_token=ACCESS_TOKEN)

    @classmethod
    def get_node_and_branches_from_web(cls, node_uuid, node_url, url_matches=None):
        try:
            status_id = url_matches

            tweet = cls.twitter.show_status(
                id=int(status_id),
                tweet_mode="extended"
            )

            node = cls.setup_node(node_url, node_data=tweet)
            branches = []

            # Get tweet media
            media = tweet['entities']['media'] if tweet['entities'].get('media') else []
            for m in media:
                branches.append({
                    'node_url': m['media_url_https'],
                    'relationship_score': 'link'
                })

            # Get tweet external links
            urls = tweet['entities'].get('urls')
            num_urls = len(urls) if urls else 0
            if num_urls > 1 or (num_urls == 1 and not tweet['is_quote_status']):
                for u in urls:
                    branches.append({
                        'node_url': u['expanded_url'],
                        'relationship_score': 'link'
                    })

            # Get quoted tweet
            if tweet['is_quote_status']:
                quoted_status_id = cls.get_quoted_status_id(tweet)
                branches.append({
                    'node_url': cls.make_path(quoted_status_id),
                    'relationship_score': 'quoted'
                })

            if tweet['in_reply_to_status_id']:
                branches.append({
                    'node_url': cls.make_path(tweet['in_reply_to_status_id']),
                    'relationship_score': 'replied_to'
                })

        except twython.exceptions.TwythonError as e:
            node = cls.setup_node(node_url, node_data=str(e), is_error=True)
            branches = []

        finally:
            return node, branches

    @classmethod
    def make_path(self, id):
        return f'https://twitter.com/i/web/status/{id}'

    @classmethod
    def get_quoted_status_id(self, tweet):
        tweet_id = tweet.get('quoted_status', {}).get('id')

        if tweet_id is None:
            tweet_id = tweet.get('quoted_status_id')

        return tweet_id

