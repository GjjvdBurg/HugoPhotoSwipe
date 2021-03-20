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

import logging
import os
import warnings
import yaml

from . import __version__
from .utils import yaml_field_to_file

# Always show deprecationwarnings
warnings.simplefilter("always", DeprecationWarning)

# HugoPhotoSwipe version
VERSION = __version__

# Filename of the settings file in working directory
SETTINGS_FILENAME = "hugophotoswipe.yml"

DEFAULTS = {
    "markdown_dir": None,
    "output_dir": None,
    "url_prefix": None,
    "output_format": "jpg",
    "dirname_large": "large",
    "dirname_small": "small",
    "dirname_thumb": "thumb",
    "dim_max_large": "1600",
    "dim_max_small": "800",
    "dim_max_thumb": "256x256",
    "dim_max_cover": "600x600",
    "cover_filename": "coverimage.jpg",
    "photo_dir": "photos",
    "album_file": "album.yml",
    "use_smartcrop_js": False,
    "smartcrop_js_path": None,
    "jpeg_progressive": False,
    "jpeg_optimize": False,
    "jpeg_quality": 75,
    "fast": False,
    "verbose": False,
}

DONT_DUMP = ["verbose", "fast"]


class Settings(object):
    def __init__(self, **entries):
        self.__dict__.update(DEFAULTS)

        # ensure dim_max is always string
        for key in entries:
            if key.startswith("dim_max_"):
                entries[key] = str(entries[key]).strip()

        self.__dict__.update(entries)

    def dump(self, dirname=None, settings_filename=None):
        """ Write settings to yaml file """
        if settings_filename is None:
            dirname = "" if dirname is None else dirname
            settings_filename = os.path.join(dirname, SETTINGS_FILENAME)
        with open(settings_filename, "w") as fp:
            fp.write("---\n")
            for key in sorted(self.__dict__.keys()):
                if key in DONT_DUMP:
                    continue
                yaml_field_to_file(fp, getattr(self, key), key)

    def validate(self):
        """ Check settings for consistency """
        prefix = "Error in settings file: "
        if self.markdown_dir is None:
            logging.error(prefix + "markdown_dir can't be empty")
            return False
        if self.output_dir is None:
            logging.error(prefix + "output_dir can't be empty")
            return False
        if self.use_smartcrop_js and self.smartcrop_js_path is None:
            logging.error(prefix + "smartcrop.js requested but path not set")
            return False
        return True


def load_settings(settings_filename=SETTINGS_FILENAME):
    data = {}
    if os.path.exists(settings_filename):
        with open(settings_filename, "r") as fp:
            data = yaml.safe_load(fp)
    return Settings(**data)


settings = load_settings()
