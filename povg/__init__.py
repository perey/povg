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
__all__ = ['context', 'matrix', 'native',
           'flatten', 'unflatten',
           'OpenVGError', 'BadHandleError', 'IllegalArgumentError',
           'OutOfMemoryError', 'PathCapabilityError',
           'UnsupportedImageFormatError', 'UnsupportedPathFormatError',
           'ImageInUseError', 'NoContextError',
           'error_codes', 'vgu_error_codes']

# Standard library imports.
from itertools import chain

# Utility function for flattening sequences of tuples.
def flatten(tuples, n=None):
    '''Flatten a sequence of tuples.

    The input sequence is flattened at the first dimension. Deeper
    nesting is not touched.
        >>> flatten(((1, 2, 3, 4), (7, 6, 5), (0,)))
        (1, 2, 3, 4, 7, 6, 5, 0)
        >>> flatten(((1, 2, (3, 4)), (7, (6, 5))))
        (1, 2, (3, 4), 7, (6, 5))

    Optionally, a tuple size n can be enforced on the data.
        >>> flatten(((1, 4, 7), (2, 5, 8), (3, 6, 9)), 3)
        (1, 4, 7, 2, 5, 8, 3, 6, 9)
        >>> flatten(((1, 4, 7), (2, 5, 8), (0, 3, 6, 9)), 3)
        Traceback (most recent call last):
            ...
        ValueError: length mismatch in sequence of tuples

    Keyword arguments:
        tuples -- The sequence of tuples to flatten.
        n -- The number of elements to enforce in each tuple. If omitted
            or None, the tuples may be of any size.
    Returns:
        A tuple containing all the elements of the tuples passed.

    '''
    if n is not None and not all(len(t) == n for t in tuples):
        raise ValueError('length mismatch in sequence of tuples')

    # Technically this isn't limited to sequences of tuples, but that's its
    # intended use in this package, and the return value will be a tuple.
    return tuple(chain.from_iterable(tuples))

# Utility function for flattening sequences of tuples.
def unflatten(seq, n, strict=True):
    '''Unflatten a tuple representing a sequence of tuples.

    By default, the tuple must contain an exact multiple of n items.
        >>> unflatten((1, 4, 7, 2, 5, 8, 3, 6, 9), 3)
        ((1, 4, 7), (2, 5, 8), (3, 6, 9))
        >>> unflatten((1, 4, 7, 2, 5, 8, 3, 6), 3)
        Traceback (most recent call last):
            ...
        ValueError: cannot evenly divide 8 items into 3-tuples

    Strict mode can be turned off, in which case any extra items will be
    put into a last tuple of less than n items.
        >>> unflatten((1, 4, 7, 2, 5, 8, 3, 6), 3, strict=False)
        ((1, 4, 7), (2, 5, 8), (3, 6))

    Keyword arguments:
        seq -- The sequence of flattened tuples.
        n -- The number of elements to put in each tuple.
        strict -- Whether to enforce tuple size. If False, any elements
            past the end of the last complete n-tuple will be placed in
            a shorter tuple. If True (the default), excess elements will
            cause a ValueError to be raised.
    Returns:
        A tuple of n-tuples.

    '''
    count, extra = divmod(len(seq), n)
    if strict and extra != 0:
        raise ValueError('cannot evenly divide {} items into '
                         '{}-tuples'.format(len(seq), n))
    tuples = tuple(tuple(seq[n * tnum:n * (tnum + 1)])
                   for tnum in range(count))
    if extra != 0:
        tail = tuple(seq[-extra:])
        return tuples + (tail,)
    else:
        return tuples


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

                   
if __name__ == '__main__':
    import doctest
    doctest.testmod()
