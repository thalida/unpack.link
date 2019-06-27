import re

from twython import Twython
import twython.exceptions

from ..base import ContentTypeBase
from . import secrets


class ContentTypeTwitter(ContentTypeBase):
    TYPE = 'twitter'
    # TODO FIND ALL THE TWITTER PATTERNS
    URL_PATTERN = re.compile(r'twitter\.com(?:.*?)status/(\d+)', re.IGNORECASE)

    auth_twitter = Twython(
        secrets.APP_KEY, secrets.APP_SECRET, oauth_version=2)
    ACCESS_TOKEN = auth_twitter.obtain_access_token()
    twitter = Twython(secrets.APP_KEY, access_token=ACCESS_TOKEN)

    @classmethod
    def get_node_and_links_from_web(cls, node_url, url_matches=None):
        try:
            status_id = url_matches

            tweet = cls.twitter.show_status(
                id=int(status_id),
                tweet_mode="extended"
            )

            node_details = cls.setup_node_details(node_data=tweet)
            links = []

            # Get tweet media
            media = tweet['entities']['media'] if tweet['entities'].get('media') else [
            ]
            for m in media:
                links.append({
                    'target_node_url': m['media_url_https'],
                    'link_type': 'link',
                })

            # Get tweet external links
            urls = tweet['entities'].get('urls')
            num_urls = len(urls) if urls else 0
            if num_urls > 1 or (num_urls == 1 and not tweet['is_quote_status']):
                for u in urls:
                    links.append({
                        'target_node_url': u['expanded_url'],
                        'link_type': 'link'
                    })

            # Get quoted tweet
            if tweet['is_quote_status']:
                quoted_status_id = cls.get_quoted_status_id(tweet)
                links.append({
                    'target_node_url': cls.make_path(quoted_status_id),
                    'link_type': 'quoted'
                })

            if tweet['in_reply_to_status_id']:
                links.append({
                    'target_node_url': cls.make_path(tweet['in_reply_to_status_id']),
                    'link_type': 'replied_to'
                })

        except twython.exceptions.TwythonError as e:
            node_details = cls.setup_node_details(
                node_data=str(e), is_error=True)
            links = []

        finally:
            return node_details, links

    @classmethod
    def make_path(self, id):
        return f'https://twitter.com/i/web/status/{id}'

    @classmethod
    def get_quoted_status_id(self, tweet):
        tweet_id = tweet.get('quoted_status', {}).get('id')

        if tweet_id is None:
            tweet_id = tweet.get('quoted_status_id')

        return tweet_id
