# -*- coding: utf-8 -*-

"""Class for albums of photos

The Album class has all the methods needed for updating albums, creating the
album markdown, etc.

Author: Gertjan van den Burg
License: GPL v3.

"""

import logging
import os
import shutil

import yaml

from tqdm import tqdm

from .config import settings
from .photo import Photo
from .utils import modtime
from .utils import question_yes_no
from .utils import yaml_field_to_file


class Album(object):
    def __init__(
        self,
        album_dir=None,
        title=None,
        album_date=None,
        properties=None,
        copyright=None,
        coverimage=None,
        creation_time=None,
        modification_time=None,
        photos=None,
        hashes=None,
    ):
        self._album_dir = album_dir
        self._album_file = None
        if self._album_dir is not None:
            self._album_file = os.path.join(album_dir, settings.album_file)

        self.title = title
        self.album_date = album_date
        self.properties = properties
        self.copyright = copyright
        self.coverimage = coverimage
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.photos = [] if photos is None else photos
        self.hashes = [] if hashes is None else hashes

    ##############
    #            #
    # Properties #
    #            #
    ##############

    @property
    def name(self):
        """Name of the album"""
        base_album_dir = os.path.basename(self._album_dir)
        return base_album_dir

    @property
    def names_unique(self):
        return len(set([p.name for p in self.photos])) == len(self.photos)

    @property
    def markdown_file(self):
        """Path of the markdown file"""
        md_dir = os.path.abspath(settings.markdown_dir)
        os.makedirs(md_dir, exist_ok=True)
        return os.path.join(md_dir, self.name + ".md")

    @property
    def output_dir(self):
        """Base dir for the processed images"""
        pth = os.path.realpath(settings.output_dir)
        return os.path.join(pth, self.name)

    ################
    #              #
    # User methods #
    #              #
    ################

    def clean(self, force=False):
        """Clean up the processed images and the markdown file

        Ask the user for confirmation and only remove if it exists

        If ``force = True``, don't ask for confirmation.
        """
        output_dir = os.path.join(settings.output_dir, self.name)
        have_md = os.path.exists(self.markdown_file)
        have_out = os.path.exists(output_dir)
        q = "Going to remove: "
        if have_md:
            q += self.markdown_file
        if have_out:
            q += " and " if have_md else ""
            q += self.output_dir
        q += ". Is this okay?"
        if (not have_md) and (not have_out):
            return
        if not force and not question_yes_no(q):
            return

        if have_md:
            logging.info(
                "[%s] Removing markdown file: %s"
                % (self.name, self.markdown_file)
            )
            os.unlink(self.markdown_file)
        if have_out:
            logging.info(
                "[%s] Removing images directory: %s" % (self.name, output_dir)
            )
            shutil.rmtree(output_dir)

    def create_markdown(self):
        """Create the markdown file, always overwrite existing"""
        # Create the header for Hugo
        coverpath = ""
        if self.coverimage is not None:
            coverpath = (
                settings.url_prefix
                + self.cover_path[len(settings.output_dir) :]
            )
            # path should always be unix style for Hugo frontmatter
            coverpath = coverpath.replace("\\", "/")

        if self.properties is None:
            proptxt = [""]
        else:
            proptxt = [
                '%s = """%s"""' % (k, v) for k, v in self.properties.items()
            ]

        txt = [
            "+++",
            'title = "%s"' % self.title,
            'date = "%s"'
            % ("" if self.album_date is None else self.album_date),
            "%s" % ("\n".join(proptxt)),
            'cover = "%s"' % coverpath,
            "+++",
            "",
            "{{< wrap >}}",  # needed to avoid <p> tags from hugo
        ]
        for photo in self.photos:
            txt.append(photo.shortcode)
            txt.append("")

        txt.append("{{< /wrap >}}")
        with open(self.markdown_file, "w") as fid:
            fid.write("\n".join(txt))
        print("Written markdown file: %s" % self.markdown_file)

    def dump(self, modification_time=None):
        """Save the album configuration to a YAML file"""
        if self._album_file is None:
            raise ValueError("Album file is not defined.")

        # create a backup first
        self._backup()

        # now overwrite the existing file
        with open(self._album_file, "w") as fid:
            fid.write("---\n")
            yaml_field_to_file(fid, self.title, "title")
            yaml_field_to_file(
                fid, self.album_date, "album_date", force_string=True
            )
            yaml_field_to_file(fid, None, "properties")
            if self.properties:
                for name, field in sorted(self.properties.items()):
                    yaml_field_to_file(fid, field, name, indent="  ")
            yaml_field_to_file(fid, self.copyright, "copyright")
            yaml_field_to_file(fid, self.coverimage, "coverimage")
            yaml_field_to_file(
                fid, self.creation_time, "creation_time", force_string=True
            )
            modification_time = modification_time or modtime()
            yaml_field_to_file(
                fid, modification_time, "modification_time", force_string=True
            )

            fid.write("\n")
            fid.write("photos:")
            for photo in self.photos:
                fid.write("\n")
                yaml_field_to_file(fid, photo.filename, "file", indent="- ")
                yaml_field_to_file(fid, photo.name, "name", indent="  ")
                yaml_field_to_file(fid, photo.alt, "alt", indent="  ")
                yaml_field_to_file(
                    fid, photo.clean_caption, "caption", indent="  "
                )

            fid.write("\n")
            fid.write("hashes:")
            for photo in self.photos:
                fid.write("\n")
                yaml_field_to_file(fid, photo.filename, "file", indent="- ")
                yaml_field_to_file(
                    fid, "sha256:" + photo.sha256sum(), "hash", indent="  "
                )
        print("Updated album file: %s" % self._album_file)

    @classmethod
    def load(cls, album_dir):
        """Load an Album class from an album directory"""
        album_file = os.path.join(album_dir, settings.album_file)
        data = {"album_dir": album_dir}
        if os.path.exists(album_file):
            with open(album_file, "r") as fid:
                data.update(yaml.safe_load(fid))
        else:
            logging.warning("Skipping non-album directory: %s" % album_dir)
            return None

        album = cls(**data)
        album.cover_path = os.path.join(
            settings.output_dir, album.name, settings.cover_filename
        )

        all_photos = []
        for p in album.photos:
            photo_path = os.path.join(album_dir, settings.photo_dir, p["file"])
            caption = (
                "" if p.get("caption", None) is None else p["caption"].strip()
            )
            alt = "" if p.get("alt", None) is None else p["alt"].strip()
            photo = Photo(
                album_name=album.name,
                original_path=photo_path,
                name=p["name"],
                alt=alt,
                caption=caption,
                copyright=album.copyright,
            )
            all_photos.append(photo)

        album.photos = []
        for photo in all_photos:
            if photo.name is None:
                logging.warning(
                    "No name defined for photo %r. Using filename." % photo
                )
                photo.name = os.path.basename(photo.original_path)
            album.photos.append(photo)
        return album

    def update(self, modification_time=None):
        """Update the processed images and the markdown file"""
        if not self.names_unique:
            logging.error(
                "Photo names for this album aren't unique. Not processing."
            )
            return

        # Make sure the list of photos from the yaml is up to date with
        # the photos in the directory, simply add all the new photos to
        # self.photos
        photo_files = [p.filename for p in self.photos]
        photo_dir = os.path.join(self._album_dir, settings.photo_dir)
        missing = [f for f in os.listdir(photo_dir) if f not in photo_files]
        missing.sort()
        for f in missing:
            photo = Photo(
                album_name=self.name,
                original_path=os.path.join(photo_dir, f),
                name=f,
                copyright=self.copyright,
            )
            self.photos.append(photo)
        logging.info(
            "[%s] Found %i photos from yaml and photos dir"
            % (self.name, len(self.photos))
        )

        # Remove the photos whose files don't exist anymore
        to_remove = []
        for photo in self.photos:
            if not os.path.exists(photo.original_path):
                to_remove.append(photo)
        for photo in to_remove:
            self.photos.remove(photo)
        logging.info(
            "[%s] Removed %i photos that have been deleted."
            % (self.name, len(to_remove))
        )

        # set the coverpath to the photo that should be the cover image
        for photo in self.photos:
            if photo.filename == self.coverimage:
                photo.cover_path = self.cover_path
            else:
                photo.cover_path = None

        # Iterate over all photos and create new resizes if they don't
        # exist yet, or the hash in self.hashes is different than the hash of
        # the current file on disk.
        photo_hashes = {}
        for photo in self.photos:
            hsh = next(
                (
                    str(h["hash"]).split(":")[-1]
                    for h in self.hashes
                    if h["file"] == photo.filename
                ),
                None,
            )
            photo_hashes[photo] = hsh

        to_process = []
        for photo in self.photos:
            if not photo.has_sizes():
                to_process.append(photo)
            elif not photo.sha256sum() == photo_hashes[photo]:
                to_process.append(photo)
            photo.free()

        logging.info(
            "[%s] There are %i photos to process."
            % (self.name, len(to_process))
        )
        if to_process:
            iterator = (
                iter(to_process)
                if not settings.verbose
                else tqdm(to_process, desc="Progress")
            )
            for photo in iterator:
                photo.create_sizes()
                photo.free()

        # Overwrite the markdown file
        logging.info("[%s] Writing markdown file." % self.name)
        self.create_markdown()

        # Overwrite the yaml file of the album
        logging.info("[%s] Saving album yaml." % self.name)
        self.dump(modification_time=modification_time)

    ####################
    #                  #
    # Internal methods #
    #                  #
    ####################

    def _backup(self):
        """Create a backup of the album file if it exists"""
        if not os.path.exists(self._album_file):
            return
        backupfile = self._album_file + ".bak"
        shutil.copy2(self._album_file, backupfile)
