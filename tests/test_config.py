# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from hugophotoswipe.config import Settings
from hugophotoswipe.config import load_settings


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        temp_fd, self._tempfile = tempfile.mkstemp("test.yml")
        os.close(temp_fd)

    def tearDown(self):
        os.unlink(self._tempfile)

    def test_config_1(self):
        settings = Settings()
        settings.dump(settings_filename=self._tempfile)

        line = lambda fp: fp.readline().strip()
        with open(self._tempfile, "r") as fp:
            self.assertEqual(line(fp), "---")
            self.assertEqual(line(fp), "album_file: album.yml")
            self.assertEqual(line(fp), "cover_filename: coverimage.jpg")
            self.assertEqual(line(fp), "dim_max_cover: 600x600")
            self.assertEqual(line(fp), "dim_max_large: 1600")
            self.assertEqual(line(fp), "dim_max_small: 800")
            self.assertEqual(line(fp), "dim_max_thumb: 256x256")
            self.assertEqual(line(fp), "dirname_large: large")
            self.assertEqual(line(fp), "dirname_small: small")
            self.assertEqual(line(fp), "dirname_thumb: thumb")
            self.assertEqual(line(fp), "exif:")
            self.assertEqual(line(fp), "iptc:")
            self.assertEqual(line(fp), "jpeg_optimize: False")
            self.assertEqual(line(fp), "jpeg_progressive: False")
            self.assertEqual(line(fp), "jpeg_quality: 75")
            self.assertEqual(line(fp), "markdown_dir:")
            self.assertEqual(line(fp), "output_dir:")
            self.assertEqual(line(fp), "output_format: jpg")
            self.assertEqual(line(fp), "photo_dir: photos")
            self.assertEqual(line(fp), "smartcrop_js_path:")
            self.assertEqual(line(fp), "tag_map:")
            self.assertEqual(line(fp), "url_prefix:")
            self.assertEqual(line(fp), "use_smartcrop_js: False")

    def test_config_2(self):
        settings = Settings(
            **dict(
                dim_max_small=500,
                jpeg_progressive=True,
                photo_dir="photo_files",
            )
        )
        settings.dump(settings_filename=self._tempfile)

        line = lambda fp: fp.readline().strip()
        with open(self._tempfile, "r") as fp:
            self.assertEqual(line(fp), "---")
            self.assertEqual(line(fp), "album_file: album.yml")
            self.assertEqual(line(fp), "cover_filename: coverimage.jpg")
            self.assertEqual(line(fp), "dim_max_cover: 600x600")
            self.assertEqual(line(fp), "dim_max_large: 1600")
            self.assertEqual(line(fp), "dim_max_small: 500")
            self.assertEqual(line(fp), "dim_max_thumb: 256x256")
            self.assertEqual(line(fp), "dirname_large: large")
            self.assertEqual(line(fp), "dirname_small: small")
            self.assertEqual(line(fp), "dirname_thumb: thumb")
            self.assertEqual(line(fp), "exif:")
            self.assertEqual(line(fp), "iptc:")
            self.assertEqual(line(fp), "jpeg_optimize: False")
            self.assertEqual(line(fp), "jpeg_progressive: True")
            self.assertEqual(line(fp), "jpeg_quality: 75")
            self.assertEqual(line(fp), "markdown_dir:")
            self.assertEqual(line(fp), "output_dir:")
            self.assertEqual(line(fp), "output_format: jpg")
            self.assertEqual(line(fp), "photo_dir: photo_files")
            self.assertEqual(line(fp), "smartcrop_js_path:")
            self.assertEqual(line(fp), "tag_map:")
            self.assertEqual(line(fp), "url_prefix:")
            self.assertEqual(line(fp), "use_smartcrop_js: False")

    def test_config_3(self):
        settings = Settings()
        self.assertFalse(settings.validate())

    def test_config_4(self):
        settings = Settings(
            **dict(
                markdown_dir="/path/to/markdown",
                output_dir="/path/to/output",
                use_smartcrop_js=True,
                smartcrop_js_path="/path/to/smartcrop.js",
            )
        )
        self.assertTrue(settings.validate())

    def test_config_5(self):
        self.maxDiff = None

        with open(self._tempfile, "w") as fp:
            fp.write("---\n")
            fp.write("album_file: album.yml\n")
            fp.write("cover_filename: coverimage.jpg\n")
            fp.write("dim_max_cover: 600x600\n")
            fp.write("dim_max_large: 1600\n")
            fp.write("dim_max_small: 500\n")
            fp.write("dim_max_thumb: 256x256\n")
            fp.write("dirname_large: large\n")
            fp.write("dirname_small: small\n")
            fp.write("dirname_thumb: thumb\n")
            fp.write("jpeg_optimize: False\n")
            fp.write("jpeg_progressive: True\n")
            fp.write("jpeg_quality: 90\n")
            fp.write("markdown_dir: /path/to/markdown\n")
            fp.write("output_dir: /path/to/output\n")
            fp.write("output_format: jpg\n")
            fp.write("photo_dir: photo_files\n")
            fp.write("smartcrop_js_path:\n")
            fp.write("url_prefix:\n")
            fp.write("use_smartcrop_js: True\n")

        settings = load_settings(settings_filename=self._tempfile)
        self.assertEqual(settings.album_file, "album.yml")
        self.assertEqual(settings.cover_filename, "coverimage.jpg")
        self.assertEqual(settings.dim_max_cover, "600x600")
        self.assertEqual(settings.dim_max_large, "1600")
        self.assertEqual(settings.dim_max_small, "500")
        self.assertEqual(settings.dim_max_thumb, "256x256")
        self.assertEqual(settings.dirname_large, "large")
        self.assertEqual(settings.dirname_small, "small")
        self.assertEqual(settings.dirname_thumb, "thumb")
        self.assertEqual(settings.jpeg_optimize, False)
        self.assertEqual(settings.jpeg_progressive, True)
        self.assertEqual(settings.jpeg_quality, 90)
        self.assertEqual(settings.markdown_dir, "/path/to/markdown")
        self.assertEqual(settings.output_dir, "/path/to/output")
        self.assertEqual(settings.output_format, "jpg")
        self.assertEqual(settings.photo_dir, "photo_files")
        self.assertEqual(settings.smartcrop_js_path, None)
        self.assertEqual(settings.url_prefix, None)
        self.assertEqual(settings.use_smartcrop_js, True)

        self.assertEqual(settings.verbose, False)
        self.assertEqual(settings.fast, False)


if __name__ == "__main__":
    unittest.main()
