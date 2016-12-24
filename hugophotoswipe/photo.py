# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import hashlib
import os
import smartcrop

from PIL import Image
from functools import total_ordering
from textwrap import wrap, indent
from subprocess import check_output

from .conf import settings
from .utils import mkdirs


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
        self.create_thumb()
        if not self.cover_path is None:
            self.create_thumb(dim=settings.dim_coverimage, pth=self.cover_path)


    def create_rescaled(self, mode):
        # open the image
        img = Image.open(self.original_path)

        # get the desired dimensions
        nwidth, nheight = self.resize_dims(mode)

        # resize the image with PIL
        nimg = img.resize((nwidth, nheight), Image.ANTIALIAS)

        pth = self.large_path if mode == 'large' else self.small_path
        nimg.save(pth)
        return pth


    def create_thumb(self, dim=None, pth=None):
        if settings.use_smartcrop_js:
            if settings.smartcrop_js_path is None:
                print("Error: smartcrop.js requested but path not set.\n"
                        "Using SmartCrop.py as fallback.")
                self.create_thumb_py(dim=dim, pth=pth)
            else:
                self.create_thumb_js(dim=dim, pth=pth)
        else:
            self.create_thumb_py(dim=dim, pth=pth)


    def create_thumb_py(self, dim=None, pth=None):
        # Load smartcrop and set options
        sc = smartcrop.SmartCrop()
        crop_options = smartcrop.DEFAULTS
        crop_options['width'] = 100
        crop_options['height'] = 100

        # Calculate the optimal crop size
        img = Image.open(self.original_path)
        if not img.mode in ['RGB', 'RGBA']:
            newimg = Image.new('RGB', img.size)
            newimg.paste(img)
            img = newimg

        ret = sc.crop(img, crop_options)
        box = (ret['topCrop']['x'],
                ret['topCrop']['y'],
                ret['topCrop']['width'] + ret['topCrop']['x'],
                ret['topCrop']['height'] + ret['topCrop']['y'])

        # Do the actual crop
        img = Image.open(self.original_path)
        nimg = img.crop(box)
        if dim is None:
            dim = settings.dim_thumbnail
        nimg.thumbnail((dim, dim), Image.ANTIALIAS)

        # Create the filename and save the thumbnail
        if pth is None:
            pth = self.thumb_path
        nimg.save(pth)
        return pth


    def create_thumb_js(self, dim=None, pth=None):
        # Load smartcrop and set options
        if dim is None:
            dim = settings.dim_thumbnail
        if pth is None:
            pth = self.thumb_path

        command = [settings.smartcrop_js_path, '--width', str(dim), '--height', 
                str(dim), self.original_path, pth]
        check_output(command)

        return pth


    def resize_dims(self, mode):
        """ Calculate the width and height of the resized image """
        if not mode in ['large', 'small', 'thumb']:
            raise ValueError("Unkown mode provided")

        if mode == 'large':
            desired_max_dim = settings.dim_max_large
        elif mode == 'small':
            desired_max_dim = settings.dim_max_small
        else:
            return (settings.dim_thumbnail, settings.dim_thumbnail)

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
            img = Image.open(self.original_path)
            self.__width = img.width
        return self.__width


    @property
    def height(self):
        if self.__height is None:
            img = Image.open(self.original_path)
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
