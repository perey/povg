#!/usr/bin/env python3

'''OpenVG 1.1 Python wrapper.'''

__version__ = '1.1' # In step with the OpenVG version wrapped.
__all__ = ['context', 'error_check', 'vg', 'vg_bool',
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

# Exceptions for OpenVG errors.
class OpenVGError(Exception):
    '''Base class for all OpenVG errors.'''
    pass
class BadHandleError(OpenVGError):
    '''An invalid handle was supplied to an OpenVG function.'''
    pass
class IllegalArgumentError(OpenVGError):
    '''An OpenVG function was given an invalid argument.'''
    pass
class OutOfMemoryError(OpenVGError):
    '''The OpenVG system could not allocate the required memory.'''
    pass
class PathCapabilityError(OpenVGError):
    '''A required OpenVG path capability was not enabled.'''
    pass
class UnsupportedImageFormatError(OpenVGError):
    '''The OpenVG implementation does not support a given image format.'''
    pass
class UnsupportedPathFormatError(OpenVGError):
    '''The OpenVG implementation does not support a given path format.'''
    pass
class ImageInUseError(OpenVGError):
    '''The supplied image is currently being used as a rendering target.'''
    pass
class NoContextError(OpenVGError):
    '''There is no current OpenVG context.'''
    pass
error_codes = {0: None, 0x1000: BadHandleError, 0x1001: IllegalArgumentError,
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
