# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

import os
import yaml
import warnings

from . import __version__
from .utils import yaml_field_to_file

# Always show deprecationwarnings
warnings.simplefilter('always', DeprecationWarning)

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
        'dim_max_thumb': 256,
        'dim_max_cover': 600,
        'square_thumbnails': True,
        'square_coverimage': True,
        'cover_filename': 'coverimage.jpg',
        'photo_dir': 'photos',
        'album_file': 'album.yml',
        'use_smartcrop_js': False,
        'smartcrop_js_path': None,
        'jpeg_progressive': False,
        'jpeg_optimize': False,
        'jpeg_quality': 75
        }


class Settings(object):
    def __init__(self, **entries):
        self.__dict__.update(DEFAULTS)

        if 'dim_thumbnail' in entries:
            warnings.warn("The 'dim_thumbnail' option has been replaced by "
                    "the 'dim_max_thumb' option in version 0.0.7. Your "
                    "hugophotoswipe.yml file will be updated.", 
                    DeprecationWarning)
            entries['dim_max_thumb'] = entries['dim_thumbnail']
            del entries['dim_thumbnail']
        if 'dim_coverimage' in entries:
            warnings.warn("The 'dim_coverimage' option has been replaced by "
                    "the 'dim_max_cover' option in version 0.0.7. Your "
                    "hugophotoswipe.yml file will be updated.", 
                    DeprecationWarning)
            entries['dim_max_cover'] = entries['dim_coverimage']
            del entries['dim_coverimage']

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
