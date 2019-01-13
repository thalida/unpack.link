import re
from pprint import pprint
from twython import Twython
import twython.exceptions
import modules.secrets as secrets
from flask import jsonify

class Unpack:
    # Patterns and stuff. Or just pattenrs actually.
    VALID_URL_PATTERN = re.compile(r'', re.IGNORECASE)

    # TODO FIND ALL THE TWITTER PATTERNS
    TWITTER_PATTERN = re.compile(r'twitter\.com(?:.*?)status/(\d+)', re.IGNORECASE)

    # TODO GET FULL LIST OF IMAGES
    # LOOK AT THE PIL LIBRARY - LINK HEADERS
    IMAGES_PATTERN = re.compile(r'\.(gif|jpe?g|tiff|png|jfif|exif|bmp|webp|svg)', re.IGNORECASE)

    TMP_ID = -1

    def __init__(self):
        auth_twitter = Twython(secrets.APP_KEY, secrets.APP_SECRET, oauth_version=2)
        ACCESS_TOKEN = auth_twitter.obtain_access_token()
        self.twitter = Twython(secrets.APP_KEY, access_token=ACCESS_TOKEN)

    def get_tree_by_id(self, id):
       pass

    def get_tree_by_path(self, path, return_type=None):
        tree = self.__fetch_tree(path)

        if return_type is 'json':
            tree = jsonify(tree)

        return tree

    def __fetch_tree(self, path):
        images_matches = self.IMAGES_PATTERN.findall(path)
        if len(images_matches) > 0:
            return self.__fetch_media_tree(images_matches[0])

        twitter_matches = self.TWITTER_PATTERN.findall(path)
        if len(twitter_matches) > 0:
            return self.__fetch_tweet_tree(int(twitter_matches[0]))

        return self.__fetch_url_tree(path)

    def __format_node(self, data=None, branches=[], num_branches=0, type=None, relationship=None, error=None):
        self.TMP_ID += 1

        node = {
            'type': type,
            'id': self.TMP_ID, 
            'data': data,
            'relationship': relationship,
            'branches': branches.copy(),
            'num_branches': num_branches,
            'has_error': False,
        }


        node['has_branches'] = node['num_branches'] > 0

        if error is not None:
            node['has_error'] = True
            node['error'] = str(error)

        return node

    def __fetch_tweet_tree(self, status_id, relationship=None, debug=False):
        try:
            tweet = self.twitter.show_status(
                id=status_id,
                tweet_mode="extended"
            )

            if debug:
                pprint(tweet)

            node = self.__format_node(data=tweet, type='tweet', relationship=relationship)
            
            # Get tweet media
            try:
                media = tweet['entities']['media'] if tweet['entities'].get('media') else []
                for m in media:
                    node['branches'].append(self.__fetch_media_tree(m['media_url_https'], relationship='link'))
                    node['num_branches'] += 1
            except Exception as e:
                print(e) # TODO add proper logging

            # Get tweet external links
            try:
                urls = tweet['entities'].get('urls')
                num_urls = len(urls) if urls else 0
                if num_urls > 1 or (num_urls == 1 and not tweet['is_quote_status']):
                    for u in urls:
                        node['branches'].append(self.__fetch_url_tree(u['expanded_url'], relationship='link'))
                        node['num_branches'] += 1
            except Exception as e:
                print(e) # TODO add proper logging

            # Get quoted tweet
            try:
                if tweet['is_quote_status']:
                    quoted_status_id = self.__get_quoted_status_id(tweet)
                    node['branches'].append(self.__fetch_tweet_tree(status_id=quoted_status_id, relationship='quoted'))
                    node['num_branches'] += 1
            except Exception as e:
                print(e) # TODO add proper logging

            # Get reply to tweet
            try:
                if tweet['in_reply_to_status_id']:
                    node['branches'].append(self.__fetch_tweet_tree(status_id=tweet['in_reply_to_status_id'], relationship='replied_to'))
                    node['num_branches'] += 1
            except Exception as e:
                print(e) # TODO add proper logging

            node['has_branches'] = node['num_branches'] > 0;
            return node
        except twython.exceptions.TwythonError as e:
            return self.__format_node(type='tweet', relationship=relationship, error=e)

    def __get_quoted_status_id(self, tweet):
        tweet_id = tweet.get('quoted_status', {}).get('id')

        if tweet_id is None:
            tweet_id = tweet.get('quoted_status_id')

        return tweet_id

    def __fetch_media_tree(self, url, relationship=None):
        # MAYBE: google image search?
        return self.__format_node(data={'url': url}, type='media', relationship=relationship)

    def __fetch_url_tree(self, url, relationship=None):
        # TODO: site scraping
        return self.__format_node(data={'url': url}, type='url', relationship=relationship)

