# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import argparse

from .hugophotoswipe import HugoPhotoSwipe


def main():
    command, album = parse_args()
    hps = HugoPhotoSwipe()
    if command == 'new':
        hps.new(name=album)
    elif command == 'update':
        hps.update(name=album)
    elif command == 'clean':
        hps.clean(name=album)
    elif command == 'init':
        hps.init()
    else:
        raise ValueError("Unknown command: %s" % command)


def parse_args():
    """ Parse the command line arguments """
    parser = argparse.ArgumentParser(
            description="Integrate Hugo and PhotoSwipe")
    parser.add_argument('command', choices=['new', 'update', 'clean', 'init'],
            help="action to do")
    parser.add_argument('album', nargs='?',
            help="album to apply the action to")
    args = parser.parse_args()
    return args.command, args.album


if __name__ == "__main__":
    exit(main())
