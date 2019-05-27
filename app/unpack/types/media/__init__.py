import re
from pprint import pprint

from ..base import TypeBase


class TypeMedia(TypeBase):
    NAME = 'media'
    NODE_TYPE = 'media'
    # figure out how to get the headers then...
    # look at the headers of the url to figure out if it's an image
    # not all images will specify their type
    URL_PATTERN = re.compile(r'(.+\.(?:gif|jpe?g|tiff|png|jfif|exif|bmp|webp|svg))$', re.IGNORECASE)
