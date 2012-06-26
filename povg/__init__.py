#!/usr/bin/env python3

'''Povg: A Python wrapper for the OpenVG 1.1 API.'''

# Copyright © 2012 Tim Pederick.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Tim Pederick'
__version__ = '0.0+1.1' # The +N.n part is the OpenVG API version wrapped.
__all__ = ['context', 'native',
           'error_check', 'vg', 'vg_bool',
           'OpenVGError', 'BadHandleError', 'IllegalArgumentError',
           'OutOfMemoryError', 'PathCapabilityError',
           'UnsupportedImageFormatError', 'UnsupportedPathFormatError',
           'ImageInUseError', 'NoContextError']

# Standard library imports.
import ctypes

# The OpenVG API.
vg = ctypes.CDLL('libOpenVG.so.1')

# Utility functions.
vg_bool = lambda val: 1 if val else 0

# Exceptions for handling OpenVG errors.
class OpenVGError(Exception):
    '''Base class for all OpenVG errors.'''
    default_msg = 'encountered an unspecified error'

    def __init__(self, msg=None):
        '''Create the exception, with a given message or the default.'''
        if msg is None:
            msg = self.default_msg
        super().__init__(msg)


class BadHandleError(OpenVGError):
    '''The handle supplied was not valid.'''
    default_msg = 'invalid handle given'


class IllegalArgumentError(OpenVGError):
    '''An invalid argument was supplied.'''
    default_msg = 'invalid argument given'


class OutOfMemoryError(OpenVGError):
    '''Insufficient memory was available for allocation.'''
    default_msg = 'insufficient memory for allocation'


class PathCapabilityError(OpenVGError):
    '''A required OpenVG path capability was not enabled.'''
    default_msg = 'required path capability not enabled'


class UnsupportedImageFormatError(OpenVGError):
    '''The OpenVG implementation does not support a given image format.'''
    default_msg = 'image format not supported'


class UnsupportedPathFormatError(OpenVGError):
    '''The OpenVG implementation does not support a given path format.'''
    default_msg = 'path format not supported'


class ImageInUseError(OpenVGError):
    '''The supplied image is currently being used as a rendering target.'''
    default_msg = 'image is being used as rendering target'


class NoContextError(OpenVGError):
    '''There is no current OpenVG context.'''
    default_msg = 'no current OpenVG context'


error_codes = {0: None, # No error.
               0x1000: BadHandleError, 0x1001: IllegalArgumentError,
               0x1002: OutOfMemoryError, 0x1003: PathCapabilityError,
               0x1004: UnsupportedImageFormatError,
               0x1005: UnsupportedPathFormatError, 0x1006: ImageInUseError,
               0x1007: NoContextError}

def error_check(fn):
    '''Check the OpenVG error trap after calling a function.'''
    def wrapped_fn(*args, **kwargs):
        result = fn(*args, **kwargs)
        errcode = error_codes.get(vg.vgGetError(), OpenVGError)
        if errcode is not None:
            raise errcode()
        return result
    return wrapped_fn
