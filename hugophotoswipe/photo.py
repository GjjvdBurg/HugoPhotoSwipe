# -*- coding: utf-8 -*-

"""Class to handle operations on individual images

The Photo class contains the methods to rescale individual images and to 
generate the shortcode for the image for the Markdown file.


Author: Gertjan van den Burg
License: GPL v3.

"""

import hashlib
import logging
import os
import smartcrop
import tempfile

from PIL.TiffImagePlugin import IFDRational
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import iptcinfo3 as iptc3
from functools import total_ordering
from textwrap import wrap
from textwrap import indent
from subprocess import check_output

from .config import settings
from .utils import cached_property

logging.getLogger('iptcinfo').setLevel('ERROR')  # Avoid warnings about missing / undecoded IPTC tags.


@total_ordering
class Photo(object):
    def __init__(
        self,
        album_name=None,
        original_path=None,
        name=None,
        alt=None,
        caption=None,
        copyright=None,
    ):
        # album
        self.album_name = album_name

        # original image properties
        self.original_path = original_path
        self.original_image_width = None
        self.original_image_height = None

        # names
        self.name = name
        self.alt = alt
        self._caption = caption

        # other
        self._copyright = copyright
        self.cover_path = None
        self._exif = None
        self._iptc = None

        # caching
        self._original_img = None

    ################
    #              #
    # User methods #
    #              #
    ################

    @property
    def original_image(self):
        """ Open original image and if needed rotate it according to EXIF """
        if not self._original_img is None:
            return self._original_img

        img = self._load_original_image()
        self._original_img = img
        return self._original_img

    def _load_original_image(self):
        img = Image.open(self.original_path)
        self._load_exif(img)
        self._load_iptc()

        # if there is no exif data, simply return the image
        exif = self._exif
        if exif is None:
            return img

        # get the orientation tag code from the ExifTags dict
        orientation = exif.get('Orientation')
        if orientation is None:
            # if no orientation is defined in the exif, return the image
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

    def free(self):
        """Manually clean up the cached image"""
        if hasattr(self, "_original_img") and self._original_img:
            self._original_img.close()
            del self._original_img
        self._original_img = None

    def _load_exif(self, image):
        if settings.exif:
            tags = set(_filter_tags(TAGS.values(),
                                    settings.exif.get('include'),
                                    settings.exif.get('exclude')))
            tags.add('Orientation')  # always need this for resize
        else:
            tags = TAGS.values()

        exif_data = {}
        exif = image._getexif() or {}
        for k, v in exif.items():
            decoded = TAGS.get(k)
            if decoded in tags and not isinstance(v, IFDRational):  # Filter complex data values
                exif_data[decoded] = v
        for k, v in exif_data.pop('GPSInfo', {}).items():
            decoded = GPSTAGS.get(k, k)
            exif_data[decoded] = v
        self._exif = exif_data

    def _load_iptc(self):
        if settings.iptc:
            tags = _filter_tags(iptc3.c_datasets_r.keys(),
                                settings.iptc.get('include'),
                                settings.iptc.get('exclude'))
        else:
            tags = iptc3.c_datasets_r.keys()

        info = iptc3.IPTCInfo(self.original_path)
        iptc = {}
        for k in tags:
            if type(info[k]) is bytes:
                iptc[k] = info[k].decode('utf-8')
            elif type(info[k]) is list:
                iptc[k] = [v.decode('utf-8') for v in info[k]]
            else:
                iptc[k] = info[k]
        self._iptc = iptc

    @property
    def exif(self):
        if not self._exif:
            _ = self.original_image  # Trigger loading image and exif data
        return self._exif

    @property
    def iptc(self):
        if not self._iptc:
            _ = self.original_image
        return self._iptc

    def _get_tag_value(self, tag):
        assert tag is not None
        try:
            obj, t = tag.split('.')
        except ValueError as e:
            raise ValueError(
                f"Tag(s) improperly formatted. "
                f"Tags should be of format iptc.<tag_name> or exif.<tag_name>. Provided: ({tag})")
        if obj.lower() not in ['exif', 'iptc']:
            raise ValueError(
                f"Tags can only reference iptc or exif data. "
                f"Tags should be of format: iptc.<tag_name> or exif.<tag_name>. Provided: ({tag})")
        o = getattr(self, obj.lower(), {})
        if o is None:
            logging.warning(f'Tag "{tag}" specified but {obj} not loaded. Returning "".')
            o = {}
        return o.get(t, "")

    @property
    def caption(self):
        if self._caption:
            return self._caption
        elif settings.tag_map and settings.tag_map.get('caption'):
            return str(self._get_tag_value(settings.tag_map.get('caption')))
        return ""

    @property
    def copyright(self):
        if self._copyright:
            return self._copyright
        elif settings.tag_map and settings.tag_map.get('copyright'):
            return str(self._get_tag_value(settings.tag_map.get('copyright')))
        return ""

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
        if (not self.cover_path is None) and (
                not os.path.exists(self.cover_path)
        ):
            return False
        return True

    def create_sizes(self):
        """ Create all necessary sizes """
        if self.name is None:
            print("Skipping file: %s. No name defined." % self.filename)
            return
        logging.info("[%s] Creating large size." % self.name)
        self.create_rescaled("large")
        logging.info("[%s] Creating small size." % self.name)
        self.create_rescaled("small")
        logging.info("[%s] Creating thumbnail size." % self.name)
        self.create_thumb(mode="thumb", pth=self.thumb_path)
        if not self.cover_path is None:
            logging.info(
                "[%s] Creating thumbnail for cover image." % self.name
            )
            self.create_thumb(mode="cover", pth=self.cover_path)

    def create_rescaled(self, mode):
        """ Do the actual resizing of images for modes without smartcrop """
        # get the desired dimensions
        nwidth, nheight = self.resize_dims(mode)
        logging.info(
            "[%s] Creating %s image of dimensions: %ix%i"
            % (self.name, mode, nwidth, nheight)
        )

        # resize the image with PIL
        nimg = self.original_image.resize((nwidth, nheight), Image.ANTIALIAS)

        pth = self.large_path if mode == "large" else self.small_path
        logging.info("[%s] Saving %s image to %s" % (self.name, mode, pth))
        if settings.output_format == "jpg":
            nimg.save(
                pth,
                optimize=settings.jpeg_optimize,
                progressive=settings.jpeg_progressive,
                quality=settings.jpeg_quality,
            )
        else:
            nimg.save(pth)
        return pth

    def create_thumb(self, mode=None, pth=None):
        """ Create the image thumbnail """
        if settings.use_smartcrop_js:
            return self.create_thumb_js(mode=mode, pth=pth)
        return self.create_thumb_py(mode=mode, pth=pth)

    def create_thumb_py(self, mode=None, pth=None):
        """ Create the thumbnail using SmartCrop.py """
        if pth is None:
            raise ValueError("path can't be None")

        # Load smartcrop and set options
        sc = smartcrop.SmartCrop()

        # Get desired dimensions
        nwidth, nheight = self.resize_dims(mode)
        factor = nwidth / 100.0

        crop_width = 100 if settings.fast else nwidth
        crop_height = int(nheight / factor) if settings.fast else nheight
        logging.info(
            "[%s] SmartCrop.py new dimensions: %ix%i"
            % (self.name, nwidth, nheight)
        )

        # Fix image mode if necessary
        img = self.original_image.copy()
        if not img.mode in ["RGB", "RGBA"]:
            newimg = Image.new("RGB", img.size)
            newimg.paste(img)
            img = newimg

        # Calculate the optimal crop size
        logging.info(
            "[%s] SmartCrop.py computing optimal crop size." % self.name
        )
        ret = sc.crop(img, crop_width, crop_height)
        box = (
            ret["top_crop"]["x"],
            ret["top_crop"]["y"],
            ret["top_crop"]["width"] + ret["top_crop"]["x"],
            ret["top_crop"]["height"] + ret["top_crop"]["y"],
        )

        # Do the actual crop
        nimg = self.original_image.crop(box)
        nimg.load()
        nimg.thumbnail((nwidth, nheight), Image.ANTIALIAS)

        # Create the filename and save the thumbnail
        logging.info("[%s] Saving SmartCrop.py thumbnail." % self.name)
        if settings.output_format == "jpg":
            nimg.save(
                pth,
                optimize=settings.jpeg_optimize,
                progressive=settings.jpeg_progressive,
                quality=settings.jpeg_quality,
            )
        else:
            nimg.save(pth)
        return pth

    def create_thumb_js(self, mode=None, pth=None):
        """ Create the thumbnail using SmartCrop.js """
        if pth is None:
            raise ValueError("path can't be None")

        # save a copy of the image with the correct orientation in a temporary
        # file
        _, tmpfname = tempfile.mkstemp(suffix="." + settings.output_format)
        self.original_image.save(tmpfname, quality=95)

        # Load smartcrop and set options
        nwidth, nheight = self.resize_dims(mode)
        logging.info(
            "[%s] SmartCrop.js new dimensions: %ix%i"
            % (self.name, nwidth, nheight)
        )
        command = [
            settings.smartcrop_js_path,
            "--width",
            str(nwidth),
            "--height",
            str(nheight),
            tmpfname,
            pth,
        ]
        logging.info("[%s] SmartCrop.js running crop command." % self.name)
        check_output(command)

        # remove the temporary file
        os.remove(tmpfname)

        return pth

    def resize_dims(self, mode):
        """ Calculate the width and height of the resized image """

        # get the setting
        if mode == "large":
            desired_max_dim = settings.dim_max_large
        elif mode == "small":
            desired_max_dim = settings.dim_max_small
        elif mode == "thumb":
            desired_max_dim = settings.dim_max_thumb
        elif mode == "cover":
            desired_max_dim = settings.dim_max_cover
        else:
            raise ValueError("Unkown mode provided")

        des_width, des_height = None, None
        if "x" in desired_max_dim:
            des_width, des_height = desired_max_dim.split("x")

        if des_width and des_height:
            nwidth = int(des_width)
            nheight = int(des_height)
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
            logging.warning(
                "[%s] Scaling up image from (%i, %i) to (%i, %i). "
                "Scaling up may not be desirable."
                % (self.name, self.width, self.height, nwidth, nheight)
            )

        return nwidth, nheight

    def sha256sum(self):
        blocksize = 65536
        hasher = hashlib.sha256()
        with open(self.original_path, "rb") as fp:
            buf = fp.read(blocksize)
            while buf:
                hasher.update(buf)
                buf = fp.read(blocksize)
        return hasher.hexdigest()

    @property
    def clean_name(self):
        """ The name of the image without extension and spaces """
        f, ext = os.path.splitext(self.name.lower().replace(" ", "_"))
        return f

    @cached_property
    def large_path(self):
        return self._get_path("large")

    @cached_property
    def small_path(self):
        return self._get_path("small")

    @cached_property
    def thumb_path(self):
        return self._get_path("thumb")

    def _get_path(self, mode):
        mode_dir = getattr(settings, f"dirname_{mode}")
        thedir = os.path.join(settings.output_dir, self.album_name, mode_dir)
        os.makedirs(thedir, exist_ok=True)
        width, height = self.resize_dims(mode)
        ext = settings.output_format
        fname = f"{self.clean_name}_{width:d}x{height:d}.{ext}"
        return os.path.join(thedir, fname)

    @property
    def clean_caption(self):
        """ Return the caption of the photo for the yaml file """
        if self.caption:
            cap = self.caption.strip()
            cap = ">\n" + indent("\n".join(wrap(cap)), " " * 10)
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
        prefix = "" if settings.url_prefix is None else settings.url_prefix
        L = len(settings.output_dir)
        large_path = (prefix + self.large_path[L:]).replace("\\", "/")
        small_path = (prefix + self.small_path[L:]).replace("\\", "/")
        thumb_path = (prefix + self.thumb_path[L:]).replace("\\", "/")
        large_dim = "%ix%i" % self.resize_dims("large")
        small_dim = "%ix%i" % self.resize_dims("small")
        thumb_dim = "%ix%i" % self.resize_dims("thumb")
        caption = "" if self.caption is None else self.caption.strip()
        copyright = "" if self.copyright is None else self.copyright.strip()
        alt = "" if self.alt is None else self.alt.strip()
        shortcode = (
            '{{{{< photo href="{large}" largeDim="{large_dim}" '
            'smallUrl="{small}" smallDim="{small_dim}" alt="{alt}" '
            'thumbSize="{thumb_dim}" thumbUrl="{thumb}" '
            'caption="{caption}" copyright="{copyright}" '
            ">}}}}"
        ).format(
            large=large_path,
            large_dim=large_dim,
            small=small_path,
            small_dim=small_dim,
            thumb=thumb_path,
            thumb_dim=thumb_dim,
            alt=alt,
            caption=caption,
            copyright=copyright,
        )
        return shortcode

    @property
    def width(self):
        """ The width of the original image """
        if self.original_image_width is None:
            self.original_image_width = self.original_image.width
        return self.original_image_width

    @property
    def height(self):
        """ The height of the original image """
        if self.original_image_height is None:
            self.original_image_height = self.original_image.height
        return self.original_image_height

    def __key(self):
        return (self.original_path, self.name, self.alt, self.caption)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        s = "Photo(original=%r, name=%r)" % (self.original_path, self.name)
        return s

    def __hash__(self):
        return int(float.fromhex(self.sha256sum()))

    def __lt__(self, other):
        return self.original_path < other.original_path

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __del__(self):
        self.free()


def _filter_tags(tags, include=None, exclude=None):
    exc = lambda k: True if not exclude else k not in exclude
    inc = lambda k: True if not include else k in include
    return filter(exc, filter(inc, tags))
