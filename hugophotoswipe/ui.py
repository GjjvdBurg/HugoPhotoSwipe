# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import argparse

from .conf import VERSION
from .hugophotoswipe import HugoPhotoSwipe


def main():
    print("This is HugoPhotoSwipe version %s" % VERSION)

    command = parse_args()

    hps = HugoPhotoSwipe()
    if command == 'new':
        hps.new()
    elif command == 'update':
        hps.update()
    elif command == 'clean':
        hps.clean()
    elif command == 'init':
        hps.init()
    else:
        raise ValueError("Unknown command: %s" % command)


def parse_args():
    """ Parse the command line arguments """
    parser = argparse.ArgumentParser(
            description="Integrate Hugo and PhotoSwipe")
    parser.add_argument('command', choices=['new', 'update', 'clean', 'init'])
    args = parser.parse_args()
    return args.command


if __name__ == "__main__":
    exit(main())
