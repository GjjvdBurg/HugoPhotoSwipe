# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import hashlib
import os
import smartcrop
import tempfile

from PIL import Image, ExifTags
from functools import total_ordering
from textwrap import wrap
from subprocess import check_output

from .conf import settings
from .utils import mkdirs

import six

if six.PY2:
    def indent(text, prefix, predicate=None):
        if predicate is None:
            def predicate(line):
                return line.strip()
        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if predicate(line) else line)
        return ''.join(prefixed_lines())
else:
    from textwrap import indent


@total_ordering
class Photo(object):

    def __init__(self, album_name=None, original_path=None, name=None, 
            alt=None, caption=None, copyright=None):
        # album
        self.album_name = album_name

        # paths
        self.original_path = original_path
        self.__large_path = None
        self.__small_path = None
        self.__thumb_path = None

        # sizes
        self.__width = None
        self.__height = None

        # names
        self.name = name
        self.alt = alt
        self.caption = caption

        # other
        self.copyright = copyright
        self.cover_path = None

    ################
    #              #
    # User methods #
    #              #
    ################

    def open_original(self):
        """ Open original image and if needed rotate it according to EXIF """
        img = Image.open(self.original_path)

        # if there is no exif data, simply return the image
        exif = img._getexif()
        if exif is None:
            return img

        # get the orientation tag code from the ExifTags dict
        orientation = next((k for k, v in ExifTags.TAGS.items() if v == 
            'Orientation'), None)
        if orientation is None:
            print("Couldn't find orientation tag in ExifTags.TAGS")
            return img

        # if no orientation is defined in the exif, return the image
        if not orientation in exif:
            return img

        # rotate the image according to the exif
        if exif[orientation] == 3:
            return img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            return img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            return img.rotate(90, expand=True)

        # fallback for unhandled rotation tags
        return img


    def has_sizes(self):
        if self.name is None:
            return False
        if not os.path.exists(self.large_path):
            return False
        if not os.path.exists(self.small_path):
            return False
        if not os.path.exists(self.thumb_path):
            return False
        if (not self.cover_path is None) and (not 
                os.path.exists(self.cover_path)):
            return False
        return True


    def create_sizes(self):
        if self.name is None:
            print("Skipping file: %s. No name defined." % self.filename)
            return
        self.create_rescaled('large')
        self.create_rescaled('small')
        self.create_thumb(mode='thumb', pth=self.thumb_path)
        if not self.cover_path is None:
            self.create_thumb(mode='cover', pth=self.cover_path)


    def create_rescaled(self, mode):
        # open the image
        img = self.open_original()

        # get the desired dimensions
        nwidth, nheight = self.resize_dims(mode)

        # resize the image with PIL
        nimg = img.resize((nwidth, nheight), Image.ANTIALIAS)

        pth = self.large_path if mode == 'large' else self.small_path
        if settings.output_format == 'jpg':
            nimg.save(pth, optimize=settings.jpeg_optimize, 
                    progressive=settings.jpeg_progressive, 
                    quality=settings.jpeg_quality)
        else:
            nimg.save(pth)
        return pth


    def create_thumb(self, mode=None, pth=None):
        if settings.use_smartcrop_js:
            if settings.smartcrop_js_path is None:
                print("Error: smartcrop.js requested but path not set.\n"
                        "Using SmartCrop.py as fallback.")
                self.create_thumb_py(mode=mode, pth=pth)
            else:
                self.create_thumb_js(mode=mode, pth=pth)
        else:
            self.create_thumb_py(mode=mode, pth=pth)


    def create_thumb_py(self, mode=None, pth=None):
        """ Create the thumbnail using SmartCrop.py """
        if pth is None:
            raise ValueError("path can't be None")

        # Load smartcrop and set options
        sc = smartcrop.SmartCrop()
        crop_options = smartcrop.DEFAULTS

        # Get desired dimensions
        nwidth, nheight = self.resize_dims(mode)
        crop_options['width'] = nwidth
        crop_options['height'] = nheight

        # Fix image mode if necessary
        img = self.open_original()
        if not img.mode in ['RGB', 'RGBA']:
            newimg = Image.new('RGB', img.size)
            newimg.paste(img)
            img = newimg

        # Calculate the optimal crop size
        ret = sc.crop(img, crop_options)
        box = (ret['topCrop']['x'],
                ret['topCrop']['y'],
                ret['topCrop']['width'] + ret['topCrop']['x'],
                ret['topCrop']['height'] + ret['topCrop']['y'])

        # Do the actual crop
        img = self.open_original()
        nimg = img.crop(box)
        nimg.thumbnail((nwidth, nheight), Image.ANTIALIAS)

        # Create the filename and save the thumbnail
        if settings.output_format == 'jpg':
            nimg.save(pth, optimize=settings.jpeg_optimize, 
                    progressive=settings.jpeg_progressive, 
                    quality=settings.jpeg_quality)
        else:
            nimg.save(pth)
        return pth


    def create_thumb_js(self, mode=None, pth=None):
        """ Create the thumbnail using SmartCrop.js """
        if pth is None:
            raise ValueError("path can't be None")

        # save a copy of the image with the correct orientation in a temporary 
        # file
        img = self.open_original()
        _, tmpfname = tempfile.mkstemp(suffix='.'+settings.output_format)
        img.save(tmpfname, quality=95)

        # Load smartcrop and set options
        nwidth, nheight = self.resize_dims(mode)
        command = [settings.smartcrop_js_path, '--width', str(nwidth), 
                '--height', str(nheight), tmpfname, pth]
        check_output(command)

        # remove the temporary file
        os.remove(tmpfname)

        return pth


    def resize_dims(self, mode):
        """ Calculate the width and height of the resized image """

        if mode == 'large':
            desired_max_dim = settings.dim_max_large
        elif mode == 'small':
            desired_max_dim = settings.dim_max_small
        elif mode == 'thumb':
            if settings.square_thumbnails:
                return (settings.dim_max_thumb, settings.dim_max_thumb)
            else:
                desired_max_dim = settings.dim_max_thumb
        elif mode == 'cover':
            if settings.square_coverimage:
                return (settings.dim_max_cover, settings.dim_max_cover)
            else:
                desired_max_dim = settings.dim_max_cover
        else:
            raise ValueError("Unkown mode provided")

        # find out the desired dimension
        maxdim = max(self.width, self.height)
        ratio = float(desired_max_dim)/float(maxdim)
        # never scale up
        ratio = min(ratio, 1.0)
        # calculate new widths
        nwidth = int(ratio * self.width)
        nheight = int(ratio * self.height)
        return nwidth, nheight


    @property
    def clean_name(self):
        return self.name.lower().replace(' ', '_')


    @property
    def large_path(self):
        if self.__large_path is None:
            thedir = os.path.join(settings.output_dir, self.album_name, 
                    settings.dirname_large)
            mkdirs(thedir)
            width, height = self.resize_dims('large')
            fname = '%s_%ix%i.%s' % (self.clean_name, width, height, 
                    settings.output_format)
            self.__large_path = os.path.join(thedir, fname)
        return self.__large_path


    @property
    def small_path(self):
        if self.__small_path is None:
            thedir = os.path.join(settings.output_dir, self.album_name, 
                    settings.dirname_small)
            mkdirs(thedir)
            width, height = self.resize_dims('small')
            fname = '%s_%ix%i.%s' % (self.clean_name, width, height, 
                    settings.output_format)
            self.__small_path = os.path.join(thedir, fname)
        return self.__small_path


    @property
    def thumb_path(self):
        if self.__thumb_path is None:
            thedir = os.path.join(settings.output_dir, self.album_name, 
                    settings.dirname_thumb)
            mkdirs(thedir)
            width, height = self.resize_dims('thumb')
            fname = '%s_%ix%i.%s' % (self.clean_name, width, height, 
                    settings.output_format)
            self.__thumb_path = os.path.join(thedir, fname)
        return self.__thumb_path


    @property
    def clean_caption(self):
        if self.caption:
            cap = self.caption.strip()
            cap = '>\n' + indent('\n'.join(wrap(cap)), ' '*10)
            return cap.strip()
        return self.caption


    @property
    def filename(self):
        return os.path.basename(self.original_path)


    @property
    def extension(self):
        return os.path.splitext(self.original_path)[-1]


    @property
    def shortcode(self):
        large_path = (settings.url_prefix +
                self.large_path[len(settings.output_dir):])
        small_path = (settings.url_prefix +
                self.small_path[len(settings.output_dir):])
        thumb_path = (settings.url_prefix +
                self.thumb_path[len(settings.output_dir):])
        large_dim = '%ix%i' % self.resize_dims('large')
        small_dim = '%ix%i' % self.resize_dims('small')
        thumb_dim = '%ix%i' % self.resize_dims('thumb')
        caption = '' if self.caption is None else self.caption.strip()
        shortcode = (
                '{{{{< photo href="{large}" largeDim="{large_dim}" '
                'smallUrl="{small}" smallDim="{small_dim}" alt="{alt}" '
                'thumbSize="{thumb_dim}" thumbUrl="{thumb}" '
                'caption="{caption}" copyright="{copyright}" '
                '>}}}}').format(
                        large=large_path, large_dim=large_dim,
                        small=small_path, small_dim=small_dim,
                        thumb=thumb_path, thumb_dim=thumb_dim,
                        alt=self.alt, caption=caption,
                        copyright=self.copyright)
        return shortcode


    @property
    def width(self):
        if self.__width is None:
            img = self.open_original()
            self.__width = img.width
        return self.__width


    @property
    def height(self):
        if self.__height is None:
            img = self.open_original()
            self.__height = img.height
        return self.__height


    def __key(self):
        return (self.original_path, self.name, self.alt, self.caption)


    def __str__(self):
        return repr(self)


    def __repr__(self):
        s = "Photo(original=%r, name=%r)" % (self.original_path, self.name)
        return s


    def __hash__(self):
        blocksize = 65536
        hasher = hashlib.sha256()
        with open(self.original_path, 'rb') as fid:
            buf = fid.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = fid.read(blocksize)
        return int(float.fromhex(hasher.hexdigest()))


    def __lt__(self, other):
        return self.original_path < other.original_path


    def __eq__(self, other):
        return self.__key() == other.__key()
