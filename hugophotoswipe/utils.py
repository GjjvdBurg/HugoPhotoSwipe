# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import errno
import os

from datetime import datetime, timezone


def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def modtime():
    # Get current time as string
    now = datetime.now(timezone.utc).astimezone()
    nowstr = now.replace(microsecond=0).isoformat()
    return nowstr


def yaml_field_to_file(fid, data, field, indent='', force_string=False):
    if data is None:
        fid.write('%s%s:\n' % (indent, field))
    else:
        if force_string:
            fid.write('%s%s: \"%s\"\n' % (indent, field, data))
        else:
            fid.write('%s%s: %s\n' % (indent, field, data))


def question_yes_no(question, default=True):
    if default:
        extension = "[Y/n]"
    else:
        extension = "[y/N]"
    while True:
        user_input = input('%s %s ' % (question, extension))
        if user_input == 'q':
            raise SystemExit
        if user_input.lower() in ['y', 'yes']:
            return True
        elif user_input.lower() in ['n', 'no']:
            return False
        elif not user_input:
            return default
        else:
            print("No valid input, please try again.")
