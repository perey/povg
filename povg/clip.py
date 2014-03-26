#!/usr/bin/env python3

'''OpenVG clipping operations (masking and clearing).

Scissoring operations are all performed through the OpenVG context, and
so are found in povg.context.

'''
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

# Masking operations.
MaskOperations = namedtuple('MaskOperations_tuple',
                            ('CLEAR', 'FILL', 'SET', 'UNION',
                             'INTERSECT', 'SUBTRACT')
                            )(*range(0x1500, 0x1506))

# TODO: Use some sort of Rectangle class or namedtuple??

# Fast clearing of the drawing surface.
def clear(pos, width, height):
    # TODO: Optional colour parameter that's set as CLEAR_COLOR before calling.
    x, y = pos
    native.vgClear(x, y, width, height)

def _mask_op(mask, op, pos, width, height):
    '''Perform a specified masking operation.'''
    x, y = pos
    native.vgMask(mask, MaskOperations.CLEAR, x, y, width, height)

def clear_mask(*args, **kwargs):
    '''Clear the current drawing mask.'''
    _mask_op(native.INVALID_HANDLE, MaskOperations.CLEAR, *args, **kwargs)

def fill_mask(*args, **kwargs):
    '''Fill the current drawing mask.'''
    _mask_op(native.INVALID_HANDLE, MaskOperations.FILL, *args, **kwargs)

def set_mask(mask, *args, **kwargs):
    '''Set the given mask or image as the current drawing mask.'''
    _mask_op(mask, MaskOperations.SET, *args, **kwargs)

def union_mask(mask, *args, **kwargs):
    '''Add the given mask or image to the current drawing mask.'''
    _mask_op(mask, MaskOperations.UNION, *args, **kwargs)

def intersect_mask(mask, *args, **kwargs):
    '''Clip the current drawing mask to the given mask or image.'''
    _mask_op(mask, MaskOperations.INTERSECT, *args, **kwargs)

def subtract_mask(mask, *args, **kwargs):
    '''Subtract the given mask or image from the current drawing mask.'''
    _mask_op(mask, MaskOperations.SUBTRACT, *args, **kwargs)

# Convenience class for mask layers.
class MaskLayer:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.mhandle = native.vgCreateMaskLayer(self.width, self.height)

    def __del__(self):
        native.vgDestroyMask(self)

    def _as_parameter_(self):
        return self.mhandle

    set_mask = set_mask
    union = union_mask
    intersect = intersect_mask
    subtract = subtract_mask

    def fill(self, value, pos=None, width=None, height=None):
        x, y = ((0, 0) if pos is None else pos)
        native.vgFillMaskLayer(self, x, y, width or self.width,
                               height or self.height, value)

    def copy(self, source_pos, dest_pos, width, height):
        sx, sy = source_pos
        dx, dy = dest_pos
        native.vgCopyMask(self, dx, dy, sx, sy, width, height)
