"""
Unit tests for the Photo class

"""

import os
import shutil
import tempfile
import unittest

from PIL import Image

from hugophotoswipe.photo import Photo
from hugophotoswipe.conf import settings


class PhotoTestCase(unittest.TestCase):
    def setUp(self):
        here = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(here, "data", "dogs", "dog-1.jpg")
        self.photo = Photo(
            album_name="test_album",
            original_path=test_file,
            name="dog_1",
            alt="Alt text",
            caption="caption text",
            copyright=None,
        )
        self._tmpdir = tempfile.mkdtemp(prefix="hps_photo_")

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def test_resize_dims(self):
        """ [Photo]: Test resize dimensions """

        # testing all possible modes
        pairs = [
            ("dim_max_large", "large"),
            ("dim_max_small", "small"),
            ("dim_max_thumb", "thumb"),
            ("dim_max_cover", "cover"),
        ]
        for setting_name, mode in pairs:
            # 1600 * 1429 / 2144 = 1066
            setattr(settings, setting_name, "1600")
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (1600, 1066))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

            # 1500 * 1429 / 2144 = 1000
            setattr(settings, setting_name, "1500x")
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (1500, 1000))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

            # 900 * 2144 / 1429 = 1500
            setattr(settings, setting_name, "x900")
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (1350, 900))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

            # exact dimensions
            setattr(settings, setting_name, "800x600")
            dims = self.photo.resize_dims(mode)
            self.assertEqual(dims, (800, 600))
            self.assertIsInstance(dims[0], int)
            self.assertIsInstance(dims[1], int)

    def test_clean_name(self):
        self.assertEqual(self.photo.clean_name, "dog_1")

    def test_paths(self):
        modes = ["large", "small", "thumb"]
        fnames = [
            "dog_1_1600x1066.jpg",
            "dog_1_800x533.jpg",
            "dog_1_256x256.jpg",
        ]

        output_dir = os.path.join(self._tmpdir, "output")
        setattr(settings, "output_dir", output_dir)

        for mode, fname in zip(modes, fnames):
            with self.subTest(mode=mode):
                exp = os.path.join(output_dir, "test_album", mode, fname)
                self.assertEqual(getattr(self.photo, mode + "_path"), exp)

    def test_filename(self):
        self.assertEqual(self.photo.filename, "dog-1.jpg")

    def test_extension(self):
        self.assertEqual(self.photo.extension, ".jpg")

    def test_clean_caption(self):
        self.assertEqual(self.photo.clean_caption, ">\n          caption text")

    def test_shortcode(self):
        output_dir = os.path.join(self._tmpdir, "output")
        url_prefix = "https://example.com/albums/"
        album_prefix = "/".join([url_prefix, "test_album"])

        setattr(settings, "output_dir", output_dir)
        setattr(settings, "url_prefix", url_prefix)
        setattr(settings, "dim_max_large", "1600")
        setattr(settings, "dim_max_small", "800")
        setattr(settings, "dim_max_thumb", "256x256")

        self.maxDiff = None

        exp_large = "/".join([album_prefix, "large", "dog_1_1600x1066.jpg"])
        exp_small = "/".join([album_prefix, "small", "dog_1_800x533.jpg"])
        exp_thumb = "/".join([album_prefix, "thumb", "dog_1_256x256.jpg"])
        exp_alt = "Alt text"
        exp_cap = "caption text"
        exp_copy = ""

        expected = (
            f'{{{{< photo href="{exp_large}" largeDim="1600x1066" '
            f'smallUrl="{exp_small}" smallDim="800x533" alt="{exp_alt}" '
            f'thumbSize="256x256" thumbUrl="{exp_thumb}" '
            f'caption="{exp_cap}" copyright="{exp_copy}" >}}}}'
        )
        self.assertEqual(self.photo.shortcode, expected)

    def test_width(self):
        self.assertEqual(self.photo.width, 2144)

    def test_height(self):
        self.assertEqual(self.photo.height, 1429)

    def test_rescaled(self):
        output_dir = os.path.join(self._tmpdir, "output")
        setattr(settings, "output_dir", output_dir)
        setattr(settings, "dim_max_large", "1600")
        setattr(settings, "dim_max_small", "800")

        modes = ["large", "small"]
        sizes = [(1600, 1066), (800, 533)]

        for mode, size in zip(modes, sizes):
            with self.subTest(mode=mode):
                out_path = self.photo.create_rescaled(mode)
                # open the image and check the size
                img = Image.open(out_path)
                self.assertEqual(img.width, size[0])
                self.assertEqual(img.height, size[1])
                img.close()

    def test_thumb(self):
        output_dir = os.path.join(self._tmpdir, "output")
        os.makedirs(output_dir)
        setattr(settings, "output_dir", output_dir)
        setattr(settings, "dim_max_thumb", "128x128")
        setattr(settings, "dim_max_cover", "400x400")
        setattr(settings, "use_smartcrop_js", False)

        modes = ["thumb", "cover"]
        sizes = [(128, 128), (400, 400)]
        names = ["thumbnail.jpg", "cover_image.jpg"]

        for mode, size, name in zip(modes, sizes, names):
            with self.subTest(mode=mode):
                pth = os.path.join(output_dir, name)
                out_path = self.photo.create_thumb(mode=mode, pth=pth)
                self.assertEqual(pth, out_path)
                img = Image.open(out_path)
                self.assertEqual(img.width, size[0])
                self.assertEqual(img.height, size[1])
                img.close()

    def test_sha256sum(self):
        self.assertEqual(self.photo.sha256sum(),
"c2fdf14c548a08032fd06e6036197fc7e9c262e6d06fac40e54ec5dd2ce6912f")


if __name__ == "__main__":
    unittest.main()
