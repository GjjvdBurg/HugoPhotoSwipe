"""
Unit tests for the Album class

"""

import os
import shutil
import tempfile
import unittest

from _constants import TEST_ALBUM_MARKDOWN_1
from _constants import TEST_ALBUM_MARKDOWN_2
from _constants import TEST_ALBUM_MARKDOWN_3
from _constants import TEST_ALBUM_MARKDOWN_4
from _constants import TEST_ALBUM_YAML_1
from _constants import TEST_ALBUM_YAML_2
from _constants import TEST_ALBUM_YAML_3
from _constants import TEST_ALBUM_YAML_4

from hugophotoswipe.album import Album
from hugophotoswipe.config import settings
from hugophotoswipe.photo import Photo


class AlbumTestCase(unittest.TestCase):
    def setUp(self):
        self._here = os.path.dirname(os.path.realpath(__file__))
        self._tmpdir = tempfile.mkdtemp(prefix="hps_album_")
        self._album_dir = os.path.join(self._tmpdir, "dogs")

        self._output_dir = os.path.join(self._tmpdir, "output")
        os.makedirs(self._album_dir)

        self._markdown_dir = os.path.join(self._tmpdir, "markdown")
        os.makedirs(self._markdown_dir)

        settings.__init__(**dict())
        setattr(settings, "output_dir", self._output_dir)
        setattr(settings, "markdown_dir", self._markdown_dir)
        setattr(settings, "url_prefix", "/hpstest/photos")

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def _make_test_album(self, album_dir):
        album_file = os.path.join(album_dir, settings.album_file)
        with open(album_file, "w") as fp:
            fp.write("---\n")
            fp.write("title: dogs\n")
            fp.write("copyright: copy\n")
            fp.write("coverimage: dog-1.jpg\n")
            fp.write("\n")
            fp.write("photos:\n")
            fp.write("- file: dog-1.jpg\n")
            fp.write("  name: dog 1\n")
            fp.write("  caption: Hello\n")
            fp.write("- file: dog-2.jpg\n")
            fp.write("  name: dog 2\n")
            fp.write("  caption: yes this is dog\n")
            fp.write("- file: dog-3.jpg\n")
            fp.write("  name:\n")
        photos_dir = os.path.join(self._album_dir, "photos")
        os.makedirs(photos_dir)

        test_dog_dir = os.path.join(self._here, "data", "dogs")
        test_dog_files = os.listdir(test_dog_dir)
        test_dogs = [os.path.join(test_dog_dir, d) for d in test_dog_files]
        for d in test_dogs:
            shutil.copy(d, photos_dir)

    def test_name(self):
        album = Album(album_dir=self._album_dir)
        self.assertEqual(album.name, "dogs")

    def test_markdown_file(self):
        album = Album(album_dir=self._album_dir)
        exp_md = os.path.join(self._markdown_dir, "dogs.md")
        self.assertEqual(album.markdown_file, exp_md)

    def test_load_empty(self):
        album_file = os.path.join(self._album_dir, settings.album_file)
        with open(album_file, "w") as fp:
            fp.write("---\n")
            fp.write("title: dogs\n")
        album = Album.load(self._album_dir)
        self.assertEqual(album._album_dir, self._album_dir)
        self.assertEqual(album.title, "dogs")
        self.assertEqual(
            album.cover_path,
            os.path.join(self._output_dir, "dogs", "coverimage.jpg"),
        )
        self.assertEqual(album.photos, [])

    def test_load_album(self):
        self._make_test_album(self._album_dir)

        album = Album.load(self._album_dir)
        self.assertEqual(len(album.photos), 3)
        for i, p in enumerate(album.photos):
            self.assertIsInstance(p, Photo)
            self.assertEqual(p.album_name, "dogs")
            if i == 2:
                # Check if missing name is handled properly
                self.assertEqual(p.name, "dog-3.jpg")
            else:
                self.assertEqual(p.name, f"dog {i+1}")
            exp_path = os.path.join(
                self._album_dir, "photos", f"dog-{i+1}.jpg"
            )
            self.assertEqual(p.original_path, exp_path)
            self.assertEqual(p.copyright, "copy")

    def test_clean(self):
        self._make_test_album(self._album_dir)

        album = Album.load(self._album_dir)
        album.update()

        md = album.markdown_file
        self.assertTrue(os.path.exists(md))
        out_album = os.path.join(self._output_dir, "dogs")
        out_large = os.path.join(out_album, "large")
        out_small = os.path.join(out_album, "small")
        out_thumb = os.path.join(out_album, "thumb")
        self.assertTrue(os.path.exists(out_album))
        self.assertTrue(os.path.exists(out_large))
        self.assertTrue(os.path.exists(out_small))
        self.assertTrue(os.path.exists(out_thumb))
        self.assertEqual(len(os.listdir(out_large)), 3)
        self.assertEqual(len(os.listdir(out_small)), 3)
        self.assertEqual(len(os.listdir(out_thumb)), 3)

        album.clean(force=True)
        self.assertFalse(os.path.exists(md))
        self.assertFalse(os.path.exists(out_album))

    def test_create_markdown(self):
        self._make_test_album(self._album_dir)
        album = Album.load(self._album_dir)
        album.create_markdown()
        self.assertTrue(os.path.exists(album.markdown_file))
        with open(album.markdown_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_MARKDOWN_1)

    def test_dump(self):
        self._make_test_album(self._album_dir)
        album = Album.load(self._album_dir)
        album.dump(modification_time="2021-03-20T16:41:06+00:00")

        album_file = os.path.join(self._album_dir, settings.album_file)
        self.assertTrue(os.path.exists(album_file + ".bak"))
        with open(album_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_YAML_1)

    def test_update_1(self):
        self._make_test_album(self._album_dir)
        album = Album.load(self._album_dir)
        album.update(modification_time="2021-03-20T16:41:06+00:00")

        # Check markdown and album files exist
        with open(album.markdown_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_MARKDOWN_1)
        with open(album._album_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_YAML_1)

        # Check Output files exist
        album_out = os.path.join(self._output_dir, "dogs")
        cover = os.path.join(album_out, "coverimage.jpg")
        resized_files = {
            "large": [
                "dog_1_1600x1066.jpg",
                "dog_2_1600x1067.jpg",
                "dog-3_1600x1040.jpg",
            ],
            "small": [
                "dog_1_800x533.jpg",
                "dog_2_800x533.jpg",
                "dog-3_800x520.jpg",
            ],
            "thumb": [
                "dog_1_256x256.jpg",
                "dog_2_256x256.jpg",
                "dog-3_256x256.jpg",
            ],
        }
        for size in resized_files:
            for file in resized_files[size]:
                filename = os.path.join(album_out, size, file)
                self.assertTrue(os.path.exists(filename))
        self.assertTrue(os.path.exists(cover))

    def test_update_2(self):
        self._make_test_album(self._album_dir)
        os.unlink(os.path.join(self._album_dir, "photos", "dog-3.jpg"))
        album = Album.load(self._album_dir)
        album.update(modification_time="2021-03-20T16:41:06+00:00")

        # Check markdown and album files exist
        with open(album.markdown_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_MARKDOWN_2)
        with open(album._album_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_YAML_2)

        # Check Output files exist
        album_out = os.path.join(self._output_dir, "dogs")
        cover = os.path.join(album_out, "coverimage.jpg")
        resized_files = {
            "large": [
                "dog_1_1600x1066.jpg",
                "dog_2_1600x1067.jpg",
            ],
            "small": [
                "dog_1_800x533.jpg",
                "dog_2_800x533.jpg",
            ],
            "thumb": [
                "dog_1_256x256.jpg",
                "dog_2_256x256.jpg",
            ],
        }
        for size in resized_files:
            for file in resized_files[size]:
                filename = os.path.join(album_out, size, file)
                self.assertTrue(os.path.exists(filename))
        self.assertTrue(os.path.exists(cover))

    def test_update_3(self):
        self._make_test_album(self._album_dir)
        cat_image = os.path.join(self._here, "data", "cats", "cat-1.jpg")
        shutil.copy(cat_image, os.path.join(self._album_dir, "photos"))

        album = Album.load(self._album_dir)
        album.update(modification_time="2021-03-20T16:41:06+00:00")

        # Check markdown and album files exist
        with open(album.markdown_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_MARKDOWN_3)
        with open(album._album_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_YAML_3)

        # Check Output files exist
        album_out = os.path.join(self._output_dir, "dogs")
        cover = os.path.join(album_out, "coverimage.jpg")
        resized_files = {
            "large": [
                "dog_1_1600x1066.jpg",
                "dog_2_1600x1067.jpg",
                "dog-3_1600x1040.jpg",
                "cat-1_1600x1068.jpg",
            ],
            "small": [
                "dog_1_800x533.jpg",
                "dog_2_800x533.jpg",
                "dog-3_800x520.jpg",
                "cat-1_800x534.jpg",
            ],
            "thumb": [
                "dog_1_256x256.jpg",
                "dog_2_256x256.jpg",
                "dog-3_256x256.jpg",
                "cat-1_256x256.jpg",
            ],
        }
        for size in resized_files:
            for file in resized_files[size]:
                filename = os.path.join(album_out, size, file)
                self.assertTrue(os.path.exists(filename))
        self.assertTrue(os.path.exists(cover))

    def test_update_4(self):
        self._make_test_album(self._album_dir)
        album = Album.load(self._album_dir)
        album.update(modification_time="2021-03-20T16:41:06+00:00")
        cat1 = os.path.join(self._here, "data", "cats", "cat-1.jpg")
        dog1 = os.path.join(self._album_dir, "photos", "dog-1.jpg")
        shutil.copy(cat1, dog1)
        album.update(modification_time="2021-03-20T16:41:06+00:00")

        # Check markdown and album files exist
        with open(album.markdown_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_MARKDOWN_4)
        with open(album._album_file, "r") as fp:
            self.assertEqual(fp.read(), TEST_ALBUM_YAML_4)

        # Check Output files exist
        album_out = os.path.join(self._output_dir, "dogs")
        cover = os.path.join(album_out, "coverimage.jpg")
        resized_files = {
            "large": [
                "dog_1_1600x1066.jpg",
                "dog_2_1600x1067.jpg",
                "dog-3_1600x1040.jpg",
            ],
            "small": [
                "dog_1_800x533.jpg",
                "dog_2_800x533.jpg",
                "dog-3_800x520.jpg",
            ],
            "thumb": [
                "dog_1_256x256.jpg",
                "dog_2_256x256.jpg",
                "dog-3_256x256.jpg",
            ],
        }
        for size in resized_files:
            for file in resized_files[size]:
                filename = os.path.join(album_out, size, file)
                self.assertTrue(os.path.exists(filename))
        self.assertTrue(os.path.exists(cover))
