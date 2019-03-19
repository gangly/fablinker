#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from __future__ import unicode_literals


class BaseError(Exception):
    """
    The base exception class for fablinker base exceptions.

    :ivar msg: The descriptive message associated with the error.
    """
    fmt = 'An unspecified error occurred'

    def __init__(self, fmt=None, **kwargs):
        if fmt is not None:
            self.fmt = fmt
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs


class ConfigParseError(BaseError):
    """
    config file error
    """
    fmt = 'Parse config file error.'


class FileNotFoundError(BaseError):
    """
    file not found
    """
    fmt = 'file not found.'


