"""
Unit tests for the Photo class

"""

from __future__ import print_function, division

import sys, os, shutil
import unittest

from hugophotoswipe.photo import Photo
from hugophotoswipe.conf import settings
from hugophotoswipe.ui import HugoPhotoSwipe, settings

class RoundTripTestCase(unittest.TestCase):

    def setUp(self):
        pth = os.path.realpath(__file__)
        dr = os.path.dirname(pth)
        dst = os.path.join(dr, 'test_gallery')
        shutil.rmtree(dst, ignore_errors=True)
        yml = os.path.join(dr, 'album.yml.test')
        dst = os.path.join(dr, 'test_gallery')
        os.makedirs(dst)
        shutil.copy(yml, os.path.join(dst, 'album.yml'))
        dst = os.path.join(dst, 'photos')
        os.makedirs(dst)
        shutil.copy(os.path.join(dr, 'test.jpg'), dst)

    def test_roundtrip(self):
        """ [Photo]: Test roundtrips don't mangle list or multiline properties
        in album.yml"""
        settings.validate()
        settings.verbose = True
        settings.fast = True
        hps = HugoPhotoSwipe()
        hps.update()
        hps = HugoPhotoSwipe()
        hps.update()
