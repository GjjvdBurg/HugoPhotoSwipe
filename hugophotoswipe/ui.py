# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import argparse
import logging

from .hugophotoswipe import HugoPhotoSwipe
from .conf import settings, SETTINGS_FILENAME

def main():
    command, album = parse_args()

    if command == 'init':
        logging.info("Dumping settings file.")
        settings.dump('.')
        print("Created settings file: %s" % SETTINGS_FILENAME)
        return

    if not settings.validate():
        return

    hps = HugoPhotoSwipe()
    if command == 'new':
        logging.info("Creating new album")
        hps.new(name=album)
    elif command == 'update':
        logging.info("Running album update")
        hps.update(name=album)
    elif command == 'clean':
        logging.info("Running clean")
        hps.clean(name=album)
    else:
        raise ValueError("Unknown command: %s" % command)
    logging.info("Dumping settings file.")
    settings.dump('.')


def parse_args():
    """ Parse the command line arguments """
    parser = argparse.ArgumentParser(
            description="Integrate Hugo and PhotoSwipe")
    parser.add_argument('-v', '--verbose', help="Verbose mode", 
            action="store_const", dest="loglevel", const=logging.INFO, 
            default=logging.WARNING)
    parser.add_argument('-f', '--fast', action="store_true", help=('Fast mode '
        '(tries less potential crops)'))
    parser.add_argument('command', choices=['new', 'update', 'clean', 'init'],
            help="action to do")
    parser.add_argument('album', nargs='?',
            help="album to apply the action to")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, datefmt="[%Y-%m-%d %H:%M:%S]",
            format="%(asctime)s - %(message)s")
    settings.verbose = args.loglevel == logging.INFO
    settings.fast = args.fast
    return args.command, args.album


if __name__ == "__main__":
    exit(main())
