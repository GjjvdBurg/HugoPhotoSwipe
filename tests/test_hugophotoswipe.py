# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from hugophotoswipe.hugophotoswipe import HugoPhotoSwipe


class HugoPhotoSwipeTestCase(unittest.TestCase):
    def setUp(self):
        self._here = os.path.dirname(os.path.realpath(__file__))
        self._tmpdir = tempfile.mkdtemp(prefix="hps_test_")
        os.chdir(self._tmpdir)

    def tearDown(self):
        os.chdir(self._here)
        shutil.rmtree(self._tmpdir)

    def test_new(self):
        hps = HugoPhotoSwipe(albums=[])
        hps.new(name="test_album")
        self.assertTrue(os.path.exists("test_album"))
        self.assertTrue(os.path.isdir("test_album"))

        photos_dir = os.path.join("test_album", "photos")
        self.assertTrue(os.path.exists(photos_dir))
        self.assertTrue(os.path.isdir(photos_dir))

        album_file = os.path.join("test_album", "album.yml")
        self.assertTrue(os.path.exists(album_file))
        with open(album_file, "r") as fp:
            self.assertEqual(fp.readline(), "---\n")
            self.assertEqual(fp.readline(), "title:\n")
            self.assertEqual(fp.readline(), "album_date:\n")
            self.assertEqual(fp.readline(), "properties:\n")
            self.assertEqual(fp.readline(), "copyright:\n")
            self.assertEqual(fp.readline(), "coverimage:\n")
            self.assertTrue(fp.readline().startswith("creation_time: "))
            self.assertTrue(fp.readline().startswith("modification_time: "))
            self.assertEqual(fp.readline(), "\n")
            self.assertEqual(fp.readline(), "photos:\n")
            self.assertEqual(fp.readline(), "hashes:")


if __name__ == "__main__":
    unittest.main()
