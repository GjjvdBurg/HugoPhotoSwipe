# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

import os
import yaml

from . import __version__
from .utils import yaml_field_to_file


# HugoPhotoSwipe version
VERSION = __version__

# Filename of the settings file in working directory
SETTINGS_FILENAME = 'hugophotoswipe.yml'

DEFAULTS = {
        'markdown_dir': None,
        'output_dir': None,
        'url_prefix': '',
        'output_format': 'jpg',
        'dirname_large': 'large',
        'dirname_small': 'small',
        'dirname_thumb': 'thumb',
        'dim_max_large': 1600,
        'dim_max_small': 800,
        'dim_thumbnail': 256,
        'dim_coverimage': 600,
        'cover_filename': 'coverimage.jpg',
        'photo_dir': 'photos',
        'album_file': 'album.yml',
        'use_smartcrop_js': False,
        'smartcrop_js_path': None,
        }


class Settings(object):
    def __init__(self, **entries):
        self.__dict__.update(DEFAULTS)
        self.__dict__.update(entries)

    def dump(self, dirname=None):
        dirname = '' if dirname is None else dirname
        pth = os.path.join(dirname, SETTINGS_FILENAME)
        with open(pth, 'w') as fid:
            fid.write('---\n')
            for key in sorted(self.__dict__.keys()):
                yaml_field_to_file(fid, getattr(self, key), key)


def load_settings():
    data = {}
    if os.path.exists(SETTINGS_FILENAME):
        with open(SETTINGS_FILENAME, 'r') as fid:
            data = yaml.safe_load(fid)
    return Settings(**data)


settings = load_settings()
