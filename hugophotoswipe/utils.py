# -*- coding: utf-8 -*-

"""Several utility functions

This file contains several utility functions used throughout HugoPhotoSwipe.

Author: Gertjan van den Burg
License: GPL v3.

"""

from __future__ import print_function

import errno
import os

import six

from datetime import datetime

if six.PY2:
    from tzlocal import get_localzone
    import pytz
    input = raw_input
else:
    from datetime import timezone


def mkdirs(path):
    """ Create directories recursively and don't complain when they exist """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def modtime():
    """ Get the current local time as a string in iso format """
    if six.PY2:
        local_tz = get_localzone()
        now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    else:
        now = datetime.now(timezone.utc).astimezone()
    nowstr = now.replace(microsecond=0).isoformat()
    return nowstr


def yaml_field_to_file(fid, data, field, indent='', force_string=False):
    """ Handy function for writing pretty yaml """
    if data is None:
        fid.write('%s%s:\n' % (indent, field))
    else:
        if force_string:
            fid.write('%s%s: \"%s\"\n' % (indent, field, data))
        else:
            fid.write('%s%s: %s\n' % (indent, field, data))


def question_yes_no(question, default=True):
    """ Ask a yes/no question from the user and be persistent """
    if default:
        extension = "[Y/n/q]"
    else:
        extension = "[y/N/q]"
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


class cached_property(object):
    """Decorator for cached class properties

    Decorator that converts a method with a single self argument into a 
    property cached on the instance.

    From Django: 
    https://github.com/django/django/blob/master/django/utils/functional.py

    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, "__doc__")
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res
