#!/usr/bin/env python3

'''Povg: A Python wrapper for the OpenVG 1.1 API.'''

# Copyright © 2013 Tim Pederick.
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
__version__ = '0.0_1.1' # The _N.n part is the OpenVG API version wrapped.
__all__ = ['context', 'native',
           'OpenVGError', 'BadHandleError', 'IllegalArgumentError',
           'OutOfMemoryError', 'PathCapabilityError',
           'UnsupportedImageFormatError', 'UnsupportedPathFormatError',
           'ImageInUseError', 'NoContextError',
           'error_codes', 'vgu_error_codes']

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


class BadWarpError(OpenVGError):
    '''There is no non-degenerate transform that meets the constraints.'''
    default_msg = 'no warp meets constraints'


error_codes = {0: None, # No error.
               0x1000: BadHandleError, 0x1001: IllegalArgumentError,
               0x1002: OutOfMemoryError, 0x1003: PathCapabilityError,
               0x1004: UnsupportedImageFormatError,
               0x1005: UnsupportedPathFormatError, 0x1006: ImageInUseError,
               0x1007: NoContextError}

vgu_error_codes = {0: None, # No error.
                   0xF000: BadHandleError, 0xF001: IllegalArgumentError,
                   0xF002: OutOfMemoryError, 0xF003: PathCapabilityError,
                   0xF004: BadWarpError}

                   
