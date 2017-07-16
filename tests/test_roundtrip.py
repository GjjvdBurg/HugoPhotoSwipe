"""
Unit tests for the Photo class

"""

from __future__ import print_function, division

import sys, os, shutil, unittest, six
import yaml, toml

# ensure we load the current hps, not the one in Python's global  site-packages
if six.PY2:
    import pytz
sys.path.insert(
  0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

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
        """ [RT]: Test roundtrips don't mangle multiline or list properties
        in album.yml"""
        settings.validate()
        settings.verbose = True
        settings.fast = True
        hps = HugoPhotoSwipe()
        hps.update()
        hps = HugoPhotoSwipe()
        hps.update()

        pth = os.path.realpath(__file__)
        dr = os.path.dirname(pth)
        dst = os.path.join(dr, 'test_gallery.md')
        toml_lines = []
        plus_count = 0
        with open(dst) as f:
          for line in f:
            if line == '+++\n':
              plus_count += 1
              if plus_count > 1:
                break
              else:
                continue
            if plus_count == 1:
              toml_lines.append(line)
        raw_toml = ''.join(toml_lines)
        front_matter = toml.loads(raw_toml)
        assert front_matter['categories']==['Stuff']
        assert front_matter['tags']==['tag1', 'tag2', 'tag3']
