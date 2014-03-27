#!/usr/bin/env python3

'''OpenVG paint management.'''

# Copyright © 2014 Tim Pederick.
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

# Local imports.
from . import native
from .params import PaintParams, param_convert
from .path import PaintModes
# TODO: Move PaintModes to somewhere more appropriate. Like here?

def current_paint(**kwargs):
    '''Get the native handle of the current paint object.

    To determine whether a given paint object is current on the OpenVG
    context, compare it for equality (not identity) with the result of
    this function.
        >>> mypaint == current_paint() # Right!
        True
        >>> mypaint is current_paint() # Wrong!
        False

    '''
    # TODO: The common code in practically every function dealing with paint
    # modes is getting a little tedious.
    fill, stroke = kwargs.get('fill'), kwargs.get('stroke')
    # Specifying neither paint mode is equivalent to specifying both.
    if not (fill or stroke):
        fill = stroke = True

    # Get the OR'd value of the requested paint modes.
    mode = ((PaintModes.FILL if fill else 0) |
            (PaintModes.STROKE if stroke else 0))

    # Sanity check.
    assert mode != 0

    # Do it!
    current = native.vgGetPaint(mode)

    # Use None in the case where no paint is set. (INVALID_HANDLE is also
    # returned on error, but an exception ought to have been raised for that.)
    return (None if current == native.INVALID_HANDLE else current)

class Paint:
    '''Represents an OpenVG paint object.

    Instance attributes:
        pthandle -- The foreign object handle for this path.

    '''
    def __init__(self):
        '''Initialise the paint object.'''
        self.pthandle = native.vgCreatePaint()

    def __del__(self):
        '''Call the native cleanup function.'''
        native.vgDestroyPaint(self)

    def __eq__(self, other):
        '''Compare two paint objects for equivalence.

        Two paint objects are considered equal if they have the same
        foreign function reference (i.e. the pthandle attribute).

        '''
        try:
            return self.pthandle == other.pthandle
        except AttributeError:
            # The other object doesn't have a pthandle.
            return False

    @property
    def _as_parameter_(self):
        '''Get the paint handle for use by foreign functions.'''
        return self.pthandle

    def _get_param(self, param):
        '''Get the value of a paint parameter.

        Keyword arguments:
            param -- The identifier of the parameter requested.

        '''
        # If param is not a known parameter type, PaintParams.details[param]
        # will raise a KeyError, which we allow to propagate upwards.
        get_fn = (native.vgGetParameterf
                  if PaintParams.details[param].values is c_float else
                  native.vgGetParameteri)
        return param_convert(param, get_fn(self, param), PaintParams)

    def set_paint(self, **kwargs):
        '''Set this paint object as current on the OpenVG context.

        The methods set_fill() and set_stroke() cover the normal use
        cases, so most applications will not need to call this directly.
        However, it can be called (with no arguments) to make this paint
        current for both fill and stroke in a single call.

        '''
        fill, stroke = kwargs.get('fill'), kwargs.get('stroke')
        # Specifying neither paint mode is equivalent to specifying both.
        if not (fill or stroke):
            fill = stroke = True

        # Get the OR'd value of the requested paint modes.
        mode = ((PaintModes.FILL if fill else 0) |
                (PaintModes.STROKE if stroke else 0))

        # Sanity check.
        assert mode != 0

        # Do it!
        native.vgSetPaint(self, mode)

    def set_fill(self):
        '''Set this paint object as the current fill paint.'''
        self.set_paint(fill=True)

    def set_stroke(self):
        '''Set this paint object as the current stroke paint.'''
        self.set_paint(stroke=True)
