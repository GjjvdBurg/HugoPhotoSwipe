# -*- coding: utf-8 -*-

"""Command line interface to HugoPhotoSwipe

"""

import sys


def main():
    from .ui import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    main()
