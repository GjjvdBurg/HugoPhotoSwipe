# -*- coding: utf-8 -*-

"""Several utility functions

This file contains several utility functions used throughout HugoPhotoSwipe.

Author: Gertjan van den Burg
License: GPL v3.

"""

from datetime import datetime
from datetime import timezone


def modtime():
    """ Get the current local time as a string in iso format """
    now = datetime.now(timezone.utc).astimezone()
    nowstr = now.replace(microsecond=0).isoformat()
    return nowstr


def yaml_field_to_file(fp, data, field, indent="", force_string=False):
    """ Handy function for writing pretty yaml """
    if data is None:
        return fp.write("%s%s:\n" % (indent, field))
    if isinstance(data, str) and len(data) == 0:
        return fp.write("%s%s:\n" % (indent, field))
    fmt = '%s%s: "%s"\n' if force_string else "%s%s: %s\n"
    fp.write(fmt % (indent, field, data))


def question_yes_no(question, default=True):
    """ Ask a yes/no question from the user and be persistent """
    extension = "[Y/n/q]" if default else "[y/N/q]"
    while True:
        user_input = input("%s %s " % (question, extension))
        if user_input == "q":
            raise SystemExit(0)

        if user_input.lower() in ["y", "yes"]:
            return True
        elif user_input.lower() in ["n", "no"]:
            return False
        elif not user_input:
            return default
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
