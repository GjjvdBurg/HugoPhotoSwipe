# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import os

from .album import Album
from .conf import settings, SETTINGS_FILENAME
from .utils import mkdirs, modtime


class HugoPhotoSwipe(object):

    def __init__(self, albums=None):
        self._albums = albums
        if self._albums is None:
            self._albums = self._load_albums()

    ################
    #              #
    # User methods #
    #              #
    ################

    def new(self):
        """ Create new album """
        name = input("Please provide a name for the new album: ")
        album_dir = name.strip().replace(' ', '_')
        if os.path.exists(album_dir):
            print("Can't create album with this name, it exists already.")
            raise SystemExit
        mkdirs(album_dir)
        mkdirs(os.path.join(album_dir, settings.photo_dir))
        album = Album(album_dir=album_dir, creation_time=modtime())
        album.dump()
        print("New album created.")


    def init(self):
        """ Initialize HugoPhotoSwipe in working dir """
        settings.dump('.')
        print("Created settings file: %s" % SETTINGS_FILENAME)


    def update(self):
        """ Update all markdown and resizes for each album """
        for album in self._albums:
            print("Updating album: %s" % album.name)
            album.update()
        print("All albums updated.")


    def clean(self):
        """ Clean up all markdown and resizes for each album """
        for album in self._albums:
            album.clean()
        print("All albums cleaned.")

    ####################
    #                  #
    # Internal methods #
    #                  #
    ####################

    def _load_albums(self):
        local_objects = os.listdir()
        local_dirs = [o for o in local_objects if os.path.isdir(o)]
        album_dirs = [d.lstrip('./') for d in local_dirs]
        albums = []
        for album_dir in album_dirs:
            album = Album.load(album_dir)
            albums.append(album)
        return albums
