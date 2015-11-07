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

# Standard library imports.
from collections import namedtuple

# Local imports.
from . import native
from .params import PaintParams, param_convert, native_getter, native_setter

# Convenience class for 32-bit, 4-component colour.
clamp_8bit = lambda x: min(255, max(0, x))
class RGBAColor(namedtuple('RGBAColor_base', ('r', 'g', 'b', 'a'))):
    '''A 4-tuple of colour values in the range [0, 255].'''
    ALPHA_BYTE, BLUE_BYTE, GREEN_BYTE, RED_BYTE = (2 ** (x * 8)
                                                   for x in range(4))
    @classmethod
    def from_int(cls, rgba):
        '''Construct from a 32-bit integer.'''
        red, gba = divmod(rgba, cls.RED_BYTE)
        green, ba = divmod(gba, cls.GREEN_BYTE)
        blue, alpha = divmod(ba, cls.BLUE_BYTE)
        # And ALPHA_BYTE == 1.
        return cls(clamp_8bit(red), clamp_8bit(green),
                   clamp_8bit(blue), clamp_8bit(alpha))

    def __int__(self):
        '''Convert to a 32-bit integer.'''
        return (clamp_8bit(self.r) * self.RED_BYTE +
                clamp_8bit(self.g) * self.GREEN_BYTE +
                clamp_8bit(self.b) * self.BLUE_BYTE +
                clamp_8bit(self.a) * self.ALPHA_BYTE)


# Paint modes.
# TODO: Bitmask?
PaintModes = namedtuple('PaintModes_tuple',
                        ('FILL', 'STROKE')
                        )(1, 2)
def kwargs_to_modes(neither_as_both=False, **kwargs):
    '''Get fill and/or stroke paint modes from keyword arguments.'''
    fill, stroke = kwargs.get('fill'), kwargs.get('stroke')

    if not fill and not stroke:
        if neither_as_both:
            return PaintModes.FILL | PaintModes.STROKE
        else:
            raise TypeError('neither fill nor stroke was set')
    else:
        return ((PaintModes.FILL if fill else 0) |
                (PaintModes.STROKE if stroke else 0))

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
    # Get the paint mode to be checked.
    mode = kwargs_to_modes(neither_as_both=True, **kwargs)

    current = native.vgGetPaint(mode)

    # Use None in the case where no paint is set. (INVALID_HANDLE is also
    # returned on error, but an exception ought to have been raised for that.)
    return (None if current == native.INVALID_HANDLE else
            Paint(pthandle=current))

class Paint:
    '''Represents an OpenVG paint object.

    Instance attributes:
        pthandle -- The foreign object handle for this path.

    '''
    def __init__(self, pthandle=None, **kwargs):
        '''Initialise the paint object.

        Keyword arguments:
            pthandle -- As the instance attribute. If provided, the new
                Paint object will be a reference to the existing OpenVG
                object indicated by the pthandle value. If omitted, a
                new OpenVG object is created.

        Keyword-only arguments:
            color -- Initialise this paint object with the given colour,
                which must be an RGBAColor instance, a 32-bit integer,
                or a four-element sequence.

        '''
        self.pthandle = (native.vgCreatePaint() if pthandle is None else
                         pthandle)
        # TODO: This should probably be the default argument, not pthandle.
        if 'color' in kwargs:
            self.color = kwargs['color']

    def __del__(self):
        '''Call the native cleanup function.'''
        # FIXME: Multiple paint objects may possess the same pthandle (e.g.
        # when calling current_paint(). Destroying one (even through garbage
        # collection) invalidates them all! Segfaults abound.
##        native.vgDestroyPaint(self)
        pass

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

    @property
    def color(self):
        '''Get the colour as an RGBAColor instance.'''
        return RGBAColor.from_int(native.vgGetColor(self))
    @color.setter
    def color(self, *values):
        '''Set the colour from an RGBAColor instance or the RGBA values.'''
        native.vgSetColor(self, int(values[0] if len(values) == 1
                                    else RGBAColor(*values)))

    def _get_param(self, param):
        '''Get the value of a paint parameter.

        Keyword arguments:
            param -- The identifier of the parameter requested.

        '''
        # If param is not a known parameter type, PaintParams.details[param]
        # will raise a KeyError, which we allow to propagate upwards.
        get_fn = native_getter(PaintParams.details[param])

        # Is it a vector type?
        if get_fn in (native.vgGetParameteriv, native.vgGetParameteriv):
            # Initialise an array to hold the values.
            value = PaintParams.details[param]()
            size = native.vgGetParameterVectorSize(self, param)
            get_fn(self, param, size, value)
        else:
            value = get_fn(self, param)
        return param_convert(param, value, PaintParams)

    def _set_param(self, param, value):
        '''Set the value of a paint parameter.

        Keyword arguments:
            param -- The identifier of the parameter being set.

        '''
        # If param is not a known parameter type, PaintParams.details[param]
        # will raise a KeyError, which we allow to propagate upwards.
        set_fn = native_getter(PaintParams.details[param])

        # Is it a vector type?
        if set_fn in (native.vgSetParameteriv, native.vgSetParameteriv):
            set_fn(self, param, len(value), value)
        else:
            set_fn(self, param, value)

    def set_paint(self, **kwargs):
        '''Set this paint object as current on the OpenVG context.

        The methods set_fill() and set_stroke() cover the normal use
        cases, so most applications will not need to call this directly.
        However, it can be called (with no arguments) to make this paint
        current for both fill and stroke in a single call.

        '''
        # Get the paint mode to set this on.
        mode = kwargs_to_modes(neither_as_both=True, **kwargs)

        # Do it!
        native.vgSetPaint(self, mode)

    def set_fill(self):
        '''Set this paint object as the current fill paint.'''
        self.set_paint(fill=True)

    def set_stroke(self):
        '''Set this paint object as the current stroke paint.'''
        self.set_paint(stroke=True)
