# -*- coding: utf-8 -*-

"""Class to handle operations on individual images

The Photo class contains the methods to rescale individual images and to 
generate the shortcode for the image for the Markdown file.


Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function, division

import hashlib
import logging
import os
import smartcrop
import tempfile

from PIL import Image, ExifTags
from functools import total_ordering
from textwrap import wrap
from subprocess import check_output

from .conf import settings
from .utils import mkdirs, cached_property

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

    @cached_property
    def original_image(self):
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
        """ Check if all necessary sizes exist on disk """
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
        """ Create all necessary sizes """
        if self.name is None:
            print("Skipping file: %s. No name defined." % self.filename)
            return
        logging.info("[%s] Creating large size." % self.name)
        self.create_rescaled('large')
        logging.info("[%s] Creating small size." % self.name)
        self.create_rescaled('small')
        logging.info("[%s] Creating thumbnail size." % self.name)
        self.create_thumb(mode='thumb', pth=self.thumb_path)
        if not self.cover_path is None:
            logging.info("[%s] Creating thumbnail for cover image." % 
                    self.name)
            self.create_thumb(mode='cover', pth=self.cover_path)


    def create_rescaled(self, mode):
        """ Do the actual resizing of images for modes without smartcrop """
        # get the desired dimensions
        nwidth, nheight = self.resize_dims(mode)
        logging.info("[%s] Creating %s image of dimensions: %ix%i" % 
                (self.name, mode, nwidth, nheight))

        # resize the image with PIL
        nimg = self.original_image.resize((nwidth, nheight), Image.ANTIALIAS)

        pth = self.large_path if mode == 'large' else self.small_path
        logging.info("[%s] Saving %s image to %s" % (self.name, mode, pth))
        if settings.output_format == 'jpg':
            nimg.save(pth, optimize=settings.jpeg_optimize, 
                    progressive=settings.jpeg_progressive, 
                    quality=settings.jpeg_quality)
        else:
            nimg.save(pth)
        return pth


    def create_thumb(self, mode=None, pth=None):
        """ Create the image thumbnail """
        if settings.use_smartcrop_js:
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
        factor = nwidth / 100.0

        crop_options['width'] = 100 if settings.fast else nwidth
        crop_options['height'] = (int(nheight / factor) if settings.fast else
            nheight)
        logging.info("[%s] SmartCrop.py new dimensions: %ix%i" % (self.name, 
            nwidth, nheight))

        # Fix image mode if necessary
        img = self.original_image.copy()
        if not img.mode in ['RGB', 'RGBA']:
            newimg = Image.new('RGB', img.size)
            newimg.paste(img)
            img = newimg

        # Calculate the optimal crop size
        logging.info("[%s] SmartCrop.py computing optimal crop size." % 
                self.name)
        ret = sc.crop(img, crop_options)
        box = (ret['topCrop']['x'],
                ret['topCrop']['y'],
                ret['topCrop']['width'] + ret['topCrop']['x'],
                ret['topCrop']['height'] + ret['topCrop']['y'])

        # Do the actual crop
        nimg = self.original_image.crop(box)
        nimg.load()
        nimg.thumbnail((nwidth, nheight), Image.ANTIALIAS)

        # Create the filename and save the thumbnail
        logging.info("[%s] Saving SmartCrop.py thumbnail." % self.name)
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
        _, tmpfname = tempfile.mkstemp(suffix='.'+settings.output_format)
        self.original_image.save(tmpfname, quality=95)

        # Load smartcrop and set options
        nwidth, nheight = self.resize_dims(mode)
        logging.info("[%s] SmartCrop.js new dimensions: %ix%i" % (self.name, 
            nwidth, nheight))
        command = [settings.smartcrop_js_path, '--width', str(nwidth), 
                '--height', str(nheight), tmpfname, pth]
        logging.info("[%s] SmartCrop.js running crop command." % self.name)
        check_output(command)

        # remove the temporary file
        os.remove(tmpfname)

        return pth


    def resize_dims(self, mode):
        """ Calculate the width and height of the resized image """

        # get the setting
        if mode == 'large':
            desired_max_dim = settings.dim_max_large
        elif mode == 'small':
            desired_max_dim = settings.dim_max_small
        elif mode == 'thumb':
            desired_max_dim = settings.dim_max_thumb
        elif mode == 'cover':
            desired_max_dim = settings.dim_max_cover
        else:
            raise ValueError("Unkown mode provided")

        des_width, des_height = None, None
        if 'x' in desired_max_dim:
            des_width, des_height = desired_max_dim.split('x')

        if des_width and des_height:
            nwidth = int(des_width)
            nheight= int(des_height)
            ratio = 0.0
        elif des_width:
            ratio = int(des_width) / self.width
            nwidth = int(des_width)
            nheight = int(round(ratio * self.height))
        elif des_height:
            ratio = int(des_height) / self.height
            nwidth = int(round(ratio * self.width))
            nheight = int(des_height)
        else:
            maxdim = max(self.width, self.height)
            ratio = int(desired_max_dim) / maxdim
            nwidth = int(round(ratio * self.width))
            nheight = int(round(ratio * self.height))

        if ratio > 1.0:
            logging.warning("[%s] Scaling up image from (%i, %i) to (%i, %i). "
                    "Scaling up may not be desirable." % (self.name, 
                        self.width, self.height, nwidth, nheight))

        return nwidth, nheight


    @property
    def clean_name(self):
        """ The name of the image without extension and spaces """
        f, ext = os.path.splitext(self.name.lower().replace(' ', '_'))
        return f


    @cached_property
    def large_path(self):
        """ The path of the large resized image """
        thedir = os.path.join(settings.output_dir, self.album_name, 
                settings.dirname_large)
        mkdirs(thedir)
        width, height = self.resize_dims('large')
        fname = '%s_%ix%i.%s' % (self.clean_name, width, height, 
                settings.output_format)
        return os.path.join(thedir, fname)


    @cached_property
    def small_path(self):
        """ The path of the small resized image """
        thedir = os.path.join(settings.output_dir, self.album_name, 
                settings.dirname_small)
        mkdirs(thedir)
        width, height = self.resize_dims('small')
        fname = '%s_%ix%i.%s' % (self.clean_name, width, height, 
                settings.output_format)
        return os.path.join(thedir, fname)


    @cached_property
    def thumb_path(self):
        """ The path of the thumbnail image """
        thedir = os.path.join(settings.output_dir, self.album_name, 
                settings.dirname_thumb)
        mkdirs(thedir)
        width, height = self.resize_dims('thumb')
        fname = '%s_%ix%i.%s' % (self.clean_name, width, height, 
                settings.output_format)
        return os.path.join(thedir, fname)


    @property
    def clean_caption(self):
        """ Return the caption of the photo for the yaml file """
        if self.caption:
            cap = self.caption.strip()
            cap = '>\n' + indent('\n'.join(wrap(cap)), ' '*10)
            return cap.strip()
        return self.caption


    @property
    def filename(self):
        """ The basename of the original path """
        return os.path.basename(self.original_path)


    @property
    def extension(self):
        """ The extension of the file """
        return os.path.splitext(self.original_path)[-1]


    @property
    def shortcode(self):
        """ Generate the shortcode for the Markdown file """
        prefix = '' if settings.url_prefix is None else settings.url_prefix
        L = len(settings.output_dir)
        large_path = (prefix + self.large_path[L:]).replace('\\','/')
        small_path = (prefix + self.small_path[L:]).replace('\\','/')
        thumb_path = (prefix + self.thumb_path[L:]).replace('\\','/')
        large_dim = '%ix%i' % self.resize_dims('large')
        small_dim = '%ix%i' % self.resize_dims('small')
        thumb_dim = '%ix%i' % self.resize_dims('thumb')
        caption = '' if self.caption is None else self.caption.strip()
        copyright = '' if self.copyright is None else self.copyright.strip()
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
                        copyright=copyright)
        return shortcode


    @property
    def width(self):
        """ The width of the original image """
        return self.original_image.width


    @property
    def height(self):
        """ The height of the original image """
        return self.original_image.height


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
