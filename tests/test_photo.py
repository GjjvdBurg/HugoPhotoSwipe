"""
Unit tests for the Photo class

"""

from __future__ import print_function, division

import os
import unittest

from hugophotoswipe.photo import Photo
from hugophotoswipe.conf import settings

class PhotoTestCase(unittest.TestCase):

    def setUp(self):
        pth = os.path.realpath(__file__)
        dr = os.path.dirname(pth)
        tst = os.path.join(dr, 'test.jpg')
        self.photo = Photo(album_name='test_album', original_path=tst, 
                name='test_image', alt='Alt text', caption='caption text', 
                copyright=None)

    def test_resize_dims(self):
        """ [Photo]: Test resize dimensions """

        # testing all possible modes
        pairs = [
                ('dim_max_large', 'large'),
                ('dim_max_small', 'small'),
                ('dim_max_thumb', 'thumb'),
                ('dim_max_cover', 'cover')
                ]
        for setting_name, mode in pairs:
            # 1040 = 1600 / 1800 * 1170
            setattr(settings, setting_name, '1600')
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (1600, 1040))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

            # 1500 / 1800 * 1170 = 975
            setattr(settings, setting_name, '1500x')
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (1500, 975))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

            # 1000 / 1170 * 1800 = 1538
            setattr(settings, setting_name, 'x1000')
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (1538, 1000))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

            # exact dimensions
            setattr(settings, setting_name, '800x600')
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (800, 600))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)
