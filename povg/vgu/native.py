#!/usr/bin/env python3

'''VGU utility library interface.'''

# Copyright © 2013 Tim Pederick.
#
# This file is part of Povg.
#
# Povg is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Povg is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Povg. If not, see <http://www.gnu.org/licenses/>.
__all__ = ['vgu_error_check', 'vguLine', 'vguPolygon', 'vguRect',
           'vguRoundRect', 'vguEllipse', 'vguArc',
           'vguComputeWarpQuadToSquare', 'vguComputeWarpSquareToQuad',
           'vguComputeWarpQuadToQuad']

# Standard library imports.
from ctypes import c_float, c_int

# Local imports.
from . import vgu_error_codes
from .. import OpenVGError
from ..native import vg, c_enum, c_handle, c_ibool, c_float_p

############## 17 (VGU) #############

# VGU functions have a distinct style of error checking, based on the return
# values of VGU functions rather than the OpenVG error trap.
def vgu_error_check(fn):
    '''Check the VGU error value returned by a function.

    Keyword arguments:
        fn -- The function to wrap with VGU error checking.

    '''
    def wrapped_fn(*args, **kwargs):
        result = fn(*args, **kwargs)
        errcode = vgu_error_codes.get(result, OpenVGError)
        if errcode is not None:
            raise errcode()
        return result
    return wrapped_fn

################ 17.1 ###############

# VGUErrorCode vguLine(VGPath path, VGfloat x0, VGfloat y0,
#                      VGfloat x1, VGfloat y1)
vg.vguLine.argtypes = (c_handle, c_float, c_float, c_float, c_float)
vg.vguLine.restype = c_enum
# Errors: BadHandleError, PathCapabilityError
vguLine = vgu_error_check(vg.vguLine)

# VGUErrorCode vguPolygon(VGPath path, const VGfloat * points, VGint count,
#                         VGboolean closed)
vg.vguPolygon.argtypes = (c_handle, c_float_p, c_int, c_ibool)
vg.vguPolygon.restype = c_enum
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vguPolygon = vgu_error_check(vg.vguPolygon)

# VGUErrorCode vguRect(VGPath path, VGfloat x, VGfloat y,
#                      VGfloat width, VGfloat height)
vg.vguRect.argtypes = (c_handle, c_float, c_float, c_float, c_float)
vg.vguRect.restype = c_enum
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vguRect = vgu_error_check(vg.vguRect)

# VGUErrorCode vguRoundRect(VGPath path, VGfloat x, VGfloat y,
#                           VGfloat width, VGfloat height,
#                           VGfloat arcWidth, VGfloat arcHeight)
vg.vguRoundRect.argtypes = (c_handle, c_float, c_float, c_float, c_float,
                            c_float, c_float)
vg.vguRoundRect.restype = c_enum
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vguRoundRect = vgu_error_check(vg.vguRoundRect)

# VGUErrorCode vguEllipse(VGPath path, VGfloat cx, VGfloat cy,
#                         VGfloat width, VGfloat height)
vg.vguEllipse.argtypes = (c_handle, c_float, c_float, c_float, c_float)
vg.vguEllipse.restype = c_enum
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vguEllipse = vgu_error_check(vg.vguEllipse)

# VGUErrorCode vguArc(VGPath path, VGfloat x, VGfloat y,
#                     VGfloat width, VGfloat height,
#                     VGfloat startAngle, VGfloat angleExtent,
#                     VGUArcType arcType)
vg.vguArc.argtypes = (c_handle, c_float, c_float, c_float, c_float, c_float,
                   c_float, c_enum)
vg.vguArc.restype = c_enum
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vguArc = vgu_error_check(vg.vguArc)

################ 17.2 ###############

# VGUErrorCode vguComputeWarpQuadToSquare(VGfloat sx0, VGfloat sy0,
#                                         VGfloat sx1, VGfloat sy1,
#                                         VGfloat sx2, VGfloat sy2,
#                                         VGfloat sx3, VGfloat sy3,
#                                         VGfloat * matrix)
vg.vguComputeWarpQuadToSquare.argtypes = (c_float, c_float, c_float, c_float,
                                          c_float, c_float, c_float, c_float,
                                          c_float_p)
vg.vguComputeWarpQuadToSquare.restype = c_enum
# Errors: IllegalArgumentError, BadWarpError
vguComputeWarpQuadToSquare = vgu_error_check(vg.vguComputeWarpQuadToSquare)

# VGUErrorCode vguComputeWarpSquareToQuad(VGfloat dx0, VGfloat dy0,
#                                         VGfloat dx1, VGfloat dy1,
#                                         VGfloat dx2, VGfloat dy2,
#                                         VGfloat dx3, VGfloat dy3,
#                                         VGfloat * matrix)
vg.vguComputeWarpSquareToQuad.argtypes = (c_float, c_float, c_float, c_float,
                                          c_float, c_float, c_float, c_float,
                                          c_float_p)
vg.vguComputeWarpSquareToQuad.restype = c_enum
# Errors: IllegalArgumentError, BadWarpError
vguComputeWarpSquareToQuad = vgu_error_check(vg.vguComputeWarpSquareToQuad)

# VGUErrorCode vguComputeWarpQuadToQuad(VGfloat dx0, VGfloat dy0,
#                                       VGfloat dx1, VGfloat dy1,
#                                       VGfloat dx2, VGfloat dy2,
#                                       VGfloat dx3, VGfloat dy3,
#                                       VGfloat sx0, VGfloat sy0,
#                                       VGfloat sx1, VGfloat sy1,
#                                       VGfloat sx2, VGfloat sy2,
#                                       VGfloat sx3, VGfloat sy3,
#                                       VGfloat * matrix)
vg.vguComputeWarpQuadToQuad.argtypes = (c_float, c_float, c_float, c_float,
                                        c_float, c_float, c_float, c_float,
                                        c_float, c_float, c_float, c_float,
                                        c_float, c_float, c_float, c_float,
                                        c_float_p)
vg.vguComputeWarpQuadToQuad.restype = c_enum
# Errors: IllegalArgumentError, BadWarpError
vguComputeWarpQuadToQuad = vgu_error_check(vg.vguComputeWarpQuadToQuad)
