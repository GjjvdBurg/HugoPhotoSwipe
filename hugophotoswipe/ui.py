# -*- coding: utf-8 -*-

"""Contains the functions for handling the user interface

This file contains the functions for handling the command line user interface.
It mainly processses the command line arguments, loads the settings,
initializes a HugoPhotoSwipe instance, and passes the command to this instance.

Author: Gertjan van den Burg
License: GPL v3.

"""

import argparse
import logging
import os
import sys

from . import __version__
from .config import SETTINGS_FILENAME
from .config import settings
from .hugophotoswipe import HugoPhotoSwipe


def main():
    """Main HugoPhotoSwipe function to be called to run the program"""
    command, album = parse_args()

    if command == "init":
        logging.info("Dumping settings file.")
        settings.dump(".")
        print("Created settings file: %s" % SETTINGS_FILENAME)
        return

    if not os.path.exists(SETTINGS_FILENAME):
        print(
            "Can't find %s, please run `hps init` to create it"
            % SETTINGS_FILENAME
        )
        raise SystemExit(1)

    if not settings.validate():
        return

    hps = HugoPhotoSwipe()
    if command == "new":
        logging.info("Creating new album")
        hps.new(name=album)
    elif command == "update":
        logging.info("Running album update")
        hps.update(name=album)
    elif command == "clean":
        logging.info("Running clean")
        hps.clean(name=album)
    else:
        raise ValueError("Unknown command: %s" % command)
    logging.info("Dumping settings file.")
    settings.dump(".")


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser(
        prog="HugoPhotoSwipe", description="Integrate Hugo and PhotoSwipe"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose mode",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-f",
        "--fast",
        action="store_true",
        help=("Fast mode (attempts fewer potential crops for thumbnails)"),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "command",
        choices=["new", "update", "clean", "init"],
        help="action to do",
    )
    parser.add_argument(
        "album", nargs="?", help="album to apply the action to"
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=args.loglevel,
        datefmt="[%Y-%m-%d %H:%M:%S]",
        format="%(asctime)s - %(message)s",
    )
    settings.verbose = args.loglevel == logging.INFO
    settings.fast = args.fast
    return args.command, args.album


if __name__ == "__main__":
    sys.exit(main())
