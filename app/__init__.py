"""Unpack

App Description

Submodules
==========

.. autosummary::
    :toctree: _autosummary

    views
    web_server
"""

import hashlib

ENV_VARS = {
    'DB': {
        'HOST': 'UNPACK_DB_HOST',
        'NAME': 'UNPACK_DB_NAME',
        'USER': 'UNPACK_DB_USER',
        'PASSWORD': 'UNPACK_DB_PASSWORD',
    }
}

def hash_url(url):
    return hashlib.md5(str(url).encode('utf-8')).hexdigest();
