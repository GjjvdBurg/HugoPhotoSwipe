# -*- coding: utf-8 -*-

"""Handle settings for HugoPhotoSwipe

HugoPhotoSwipe uses a settings file for the configuration set by the user. This 
configuration is loaded/initialized here as a ``settings`` object and is used 
throughout the program. 

Flags to the ``hps`` executable are saved as settings as well, but are not 
dumped to the yaml file because they are runtime options.

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
        'url_prefix': None,
        'output_format': 'jpg',
        'dirname_large': 'large',
        'dirname_small': 'small',
        'dirname_thumb': 'thumb',
        'dim_max_large': '1600',
        'dim_max_small': '800',
        'dim_max_thumb': '256x256',
        'dim_max_cover': '600x600',
        'cover_filename': 'coverimage.jpg',
        'photo_dir': 'photos',
        'album_file': 'album.yml',
        'use_smartcrop_js': False,
        'smartcrop_js_path': None,
        'jpeg_progressive': False,
        'jpeg_optimize': False,
        'jpeg_quality': 75
        }

DONT_DUMP = ['verbose', 'fast']

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

        # remove deprecated square options
        square_options = ['square_thumbnails', 'square_coverimage']
        square_dim_opts = {'square_thumbnails': 'dim_max_thumb',
                'square_coverimage': 'dim_max_cover'}
        for opt in square_options:
            if opt in entries:
                warnings.warn("The '%s' option has been removed "
                    "because of the new size syntax of version 0.0.15. Your "
                    "hugophotoswipe.yml file will be updated." % opt,
                    DeprecationWarning)
                if entries[opt]:
                    dim = entries[square_dim_opts[opt]]
                    entries[square_dim_opts[opt]] = '%ix%i' % (dim, dim)
                del entries[opt]

        # ensure dim_max is always string
        for key in entries:
            if key.startswith('dim_max_'):
                entries[key] = str(entries[key]).strip()

        self.__dict__.update(entries)

    def dump(self, dirname=None):
        """ Write settings to yaml file """
        dirname = '' if dirname is None else dirname
        pth = os.path.join(dirname, SETTINGS_FILENAME)
        with open(pth, 'w') as fid:
            fid.write('---\n')
            for key in sorted(self.__dict__.keys()):
                if key in DONT_DUMP:
                    continue
                yaml_field_to_file(fid, getattr(self, key), key)

    def validate(self):
        """ Check settings for consistency """
        prefix = "Error in settings file: "
        if self.markdown_dir is None:
            print(prefix + "markdown_dir can't be empty")
            return False
        if self.output_dir is None:
            print(prefix + "output_dir can't be empty")
            return False
        if self.use_smartcrop_js and self.smartcrop_js_path is None:
            print(prefix + "smartcrop.js requested but path not set")
            return False
        return True


def load_settings():
    data = {}
    if os.path.exists(SETTINGS_FILENAME):
        with open(SETTINGS_FILENAME, 'r') as fid:
            data = yaml.safe_load(fid)
    return Settings(**data)


settings = load_settings()
