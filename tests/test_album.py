"""
Unit tests for the Photo class

"""

from __future__ import print_function, division

import os
import unittest
from time import sleep
from unittest.mock import patch

from hugophotoswipe.album import Album
from hugophotoswipe.conf import settings


class AlbumTestCase(unittest.TestCase):

    def setUp(self):
        pth = os.path.dirname(os.path.realpath(__file__))
        dr = os.path.join(pth, 'album')
        try:
            os.makedirs(os.path.join(pth, 'parking'))
        except FileExistsError:
            pass

        test_settings = {
            'photo_dir': 'photos',
            'album_file': 'album.yml',
            'output_dir': os.path.join(pth, 'test_output', 'output'),
            'markdown_dir': os.path.join(pth, 'test_output', 'markdown'),
            'verbose': False,
            'fast': False,
            # cover_filename: coverimage.jpg
            # url_prefix: /galleries
            # generate_branch_bundle: True
            # iptc: {'dump': True}
            # output_format: jpg
            # tag_map: {'tags': 'iptc.keywords', 'caption': 'iptc.object name', 'copyright': 'exif.Artist'}
        }

        for k, v in test_settings.items():
            setattr(settings, k, v)

        self.album = Album.load(dr)

    def tearDown(self):
        import shutil

        pth = os.path.dirname(os.path.realpath(__file__))
        dr = os.path.join(pth, 'album')
        parking = os.path.join(pth, 'parking')

        # move photo back
        if os.path.exists(os.path.join(parking, 'test.jpg')):
            os.replace(os.path.join(parking, 'test.jpg'), os.path.join(dr, settings.photo_dir, 'test.jpg'))

        shutil.rmtree(parking, ignore_errors=True)
        shutil.rmtree(os.path.join(pth, 'test_output'), ignore_errors=True)
        shutil.rmtree(os.path.join(dr, f'{settings.album_file}.bak'), ignore_errors=True)

    def test_generates_correct_output_files(self):
        """ Confirm update() generates expected set of files. """
        import tracemalloc
        tracemalloc.start()

        md_d = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), settings.markdown_dir)
        out_d = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), settings.output_dir)

        self.album.update()
        output_files = {
            'album_markdown': os.path.join(md_d, 'album.md'),
            'large_jpg': os.path.join(out_d, 'album', 'large', f'test_1600x1040.jpg'),
            'small_jpg': os.path.join(out_d, 'album', 'small', f'test_800x520.jpg'),
            'thumb_jpg': os.path.join(out_d, 'album', 'thumb', f'test_256x256.jpg'),
        }

        system_files = _get_output_files()
        self.assertCountEqual(output_files.values(), system_files, "Output files don't match expected set.")

    def test_handles_photo_delete(self):
        """ [Album]: Handle removing a photo file after generating the album """
        import yaml

        album_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'album', settings.album_file)

        self.album.update()
        self.assertTrue(os.path.exists(album_file))

        photo_d = os.path.join(os.path.dirname(album_file), settings.photo_dir)
        parking = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'parking')

        # remove photo and update
        while os.path.exists(os.path.join(photo_d, 'test.jpg')):
            try:
                os.replace(os.path.join(photo_d, 'test.jpg'), os.path.join(parking, 'test.jpg'))
            except PermissionError:
                print('File locked. Waiting for a second.')
                sleep(1)
        self.album.update()
        self.assertTrue(os.path.exists(album_file))

        with open(album_file, 'r') as f:
            md_data = yaml.safe_load(f)
        hashes = md_data.get('hashes')
        self.assertIsNone(hashes, "Hash was not removed from album.yml when source photo was deleted.")

        # Current version does not guarantee deleting output photos of deleted source files.
        # output_files = {
        #     'album_markdown': os.path.join(md_d, 'album.md'),
        # }
        # system_files = _get_output_files()
        # self.assertCountEqual(output_files.values(), system_files,
        #                       "Output files don't match expected set upon delete of source photo.")

        # return photo to original location
        os.replace(os.path.join(parking, 'test.jpg'), os.path.join(photo_d, 'test.jpg'))

    @patch('six.moves.input', return_value='y')
    def test_clean_removes_all(self, mocked):
        """ confirm clean() removes all output """
        self.album.update()
        self.album.clean()

        output_files = {}
        system_files = _get_output_files()
        print(system_files)
        self.assertCountEqual(output_files.values(), system_files,
                              "Album.clean() did not remove all output or markdown files.")


def _get_output_files(base_dir=None, dirs=None):
    dirs = dirs or [settings.markdown_dir, settings.output_dir]
    base_dir = base_dir or os.path.dirname(os.path.realpath(__file__))

    output_files = []
    for d in dirs:
        output_files.extend(os.walk(os.path.join(base_dir, d)))

    files_with_path = []
    for r, _, files in output_files:
        for file in files:
            files_with_path.append(os.path.join(r, file))

    return files_with_path
