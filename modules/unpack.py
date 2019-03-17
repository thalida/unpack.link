import re
from pprint import pprint
from twython import Twython
import twython.exceptions
import modules.secrets as secrets
from flask import jsonify

# add reddit using their api
# add insta (check if they have one?)
# add any url (every single href on the page + the meta data)

class TypeBase():
    def setup_node(self, data=None, branches=[], num_branches=0, node_type=None, relationship=None, error=None):
        node = {
            'type': node_type,
            'data': data,
            'relationship': relationship,
            'branches': branches.copy(),
            'num_branches': num_branches,
            'has_error': False,
        }

        if error is not None:
            node['has_error'] = True
            node['error'] = str(error)

        return node


class TypeMedia(TypeBase):
    # figure out how to get the headers then...
    # look at the headers of the url to figure out if it's an image
    # not all images will specify their type
    URL_PATTERN = re.compile(r'\.(gif|jpe?g|tiff|png|jfif|exif|bmp|webp|svg)', re.IGNORECASE)

    def fetch(self, url, relationship=None):
        # MAYBE: google image search?
        return self.setup_node(data={'url': url}, node_type='media', relationship=relationship), None


class TypeGeneric(TypeBase):
    URL_PATTERN = re.compile(r'', re.IGNORECASE)

    def fetch(self, url, relationship=None):
        # MAYBE: google image search?
        return self.setup_node(data={'url': url}, node_type='url', relationship=relationship), None


class TypeTwitter(TypeBase):
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

            branch_urls = []

            # Get tweet media
            media = tweet['entities']['media'] if tweet['entities'].get('media') else []
            for m in media:
                branch_urls.append({
                    'url': m['media_url_https'],
                    'relationship': 'link'
                })

            # Get tweet external links
            urls = tweet['entities'].get('urls')
            num_urls = len(urls) if urls else 0
            if num_urls > 1 or (num_urls == 1 and not tweet['is_quote_status']):
                for u in urls:
                    branch_urls.append({
                        'url': u['expanded_url'],
                        'relationship': 'link'
                    })

            # Get quoted tweet
            if tweet['is_quote_status']:
                quoted_status_id = self.__get_quoted_status_id(tweet)
                branch_urls.append({
                    'url': self.__make_path(quoted_status_id),
                    'relationship': 'quoted'
                })

            if tweet['in_reply_to_status_id']:
                branch_urls.append({
                    'url': self.__make_path(tweet['in_reply_to_status_id']),
                    'relationship': 'replied_to'
                })

            return node, branch_urls
        except twython.exceptions.TwythonError as e:
            return self.setup_node(node_type='tweet', relationship=relationship, error=e), None


    def __make_path(self, id):
        return f'https://twitter.com/i/web/status/{id}'

    def __get_quoted_status_id(self, tweet):
        tweet_id = tweet.get('quoted_status', {}).get('id')

        if tweet_id is None:
            tweet_id = tweet.get('quoted_status_id')

        return tweet_id


class Unpack:
    def __init__(self):
        self.types = {
            'twitter': TypeTwitter(),
            'meda': TypeMedia(),
            'generic': TypeGeneric()
        }

    def get_tree_by_path(self, path, return_type=None):
        tree = self.__fetch_tree(path)

        if return_type is 'json':
            tree = jsonify(tree)

        return tree

    def __fetch_tree(self, resource, relationship=None):
        res = None

        for t, c in self.types.items():
            if t is 'generic':
                continue

            matches = c.URL_PATTERN.findall(resource)
            if len(matches) > 0:
                res = {'type': t, 'item': matches[0]}
                break

        if res is None:
            res = {'type': 'generic', 'item': resource}

        tree, branch_urls = self.types[res['type']].fetch(res['item'])
        return self.__fetch_branches(tree, branch_urls)

    def __fetch_branches(self, tree, branch_urls):
        if branch_urls is None:
            branch_urls = []

        tree['num_branches'] = len(branch_urls)
        tree['has_branches'] = tree['num_branches'] > 0

        for branch in branch_urls:
            try:
                tree['branches'].append(
                    self.__fetch_tree(branch['url'], relationship=branch['relationship'])
                )
            except Exception as e:
                print(e) # TODO add proper logging

        return tree

