# -*- coding: utf-8 -*-

"""The main HugoPhotoSwipe class

This file contains the HugoPhotoSwipe class which is handles the command line 
user interface commands through several methods. It handles creation of new 
albums, updating albums, and cleaning albums.

Author: Gertjan van den Burg
License: GPL v3.

"""

import logging
import os

from .album import Album
from .config import settings
from .utils import modtime


class HugoPhotoSwipe(object):
    def __init__(self, albums=None):
        self._albums = self._load_albums() if albums is None else albums

    ################
    #              #
    # User methods #
    #              #
    ################

    def new(self, name=None):
        """ Create new album """
        if name is None:
            name = input("Please provide a name for the new album: ")

        album_dir = name.strip().rstrip("/").replace(" ", "_")
        if os.path.exists(album_dir):
            print("Can't create album with this name, it exists already.")
            raise SystemExit(1)

        logging.info("Creating album directory")
        os.makedirs(album_dir, exist_ok=True)

        logging.info("Creating album photos directory")
        os.makedirs(os.path.join(album_dir, settings.photo_dir), exist_ok=True)

        album = Album(album_dir=album_dir, creation_time=modtime())
        logging.info("Saving album yaml")
        album.dump()
        print("New album created.")

    def update(self, name=None):
        """ Update all markdown and resizes for each album """
        self.update_all() if name is None else self.update_single(name)

    def update_all(self):
        for album in self._albums:
            print("Updating album: %s" % album.name)
            album.update()
        print("All albums updated.")

    def update_single(self, name):
        name = name.strip("/")
        album = next((a for a in self._albums if a.name == name), None)
        if album is None:
            print("Couldn't find album with name %s. Stopping." % name)
            raise SystemExit(1)
        album.update()
        print("Album %s updated." % album.name)

    def clean(self, name=None):
        """ Clean up all markdown and resizes for each album """
        self.clean_all() if name is None else self.clean_single(name)

    def clean_all(self):
        for album in self._albums:
            album.clean()
        print("All albums cleaned.")

    def clean_single(self, name):
        name = name.strip("/")
        album = next((a for a in self._albums if a.name == name), None)
        if album is None:
            print("Couldn't find album with name %s. Stopping." % name)
            raise SystemExit(1)
        album.clean()
        print("Album %s cleaned." % album.name)

    ####################
    #                  #
    # Internal methods #
    #                  #
    ####################

    def _load_albums(self):
        """ Load all albums from the current directory """
        local_objects = os.listdir(".")
        local_dirs = [o for o in local_objects if os.path.isdir(o)]
        album_dirs = [d.lstrip("./") for d in local_dirs]
        albums = []
        for album_dir in album_dirs:
            logging.info("Loading album from dir: %s" % album_dir)
            album = Album.load(album_dir)
            if album is None:
                continue
            albums.append(album)
        return albums
