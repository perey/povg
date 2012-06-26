#!/usr/bin/env python3

'''OpenVG library interface.'''

# Copyright © 2012 Tim Pederick.
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
__all__ = ['vgFlush',
           'INVALID_HANDLE']

# Standard library imports.
from ctypes import (CDLL, c_byte, c_ubyte, c_short, c_int, c_uint, c_float,
                    c_void_p, POINTER)

# Local imports.
from . import VGError, error_codes

# Native library import.
vg = ctypes.CDLL('libOpenVG.so.1') # TODO: Cross-platform loading.
int_p, float_p, ubyte_p = POINTER(c_int), POINTER(c_float), POINTER(c_ubyte)

# Type definitions.
vbool = enum = bitfield = vhandle = c_uint

INVALID_HANDLE = vhandle(0)

# Trap EGL errors. We set the argument and return types for
# "VGErrorCode vgGetError(void)" here, since we use it for error_check.
vg.vgGetError.argtypes = ()
vg.vgGetError.restype = enum

def error_check(fn):
    '''Check the OpenVG error trap after calling a function.'''
    def wrapped_fn(*args, **kwargs):
        result = fn(*args, **kwargs)
        errcode = error_codes.get(vg.vgGetError(), OpenVGError)
        if errcode is not None:
            raise errcode()
        return result
    return wrapped_fn

# Set argument and return types, and wrap with error checking. Functions are
# listed by their order in the OpenVG 1.1 specification, with section numbers.
# All(?) functions may cause an OutOfMemoryError, so these aren't listed here.

################ 4.3 ################

# void vgFlush(void)
vg.vgFlush.argtypes = ()
vg.vgFlush.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgFlush = error_check(vg.vgFlush)

# void vgFinish(void)
vg.vgFinish.argtypes = ()
vg.vgFinish.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgFinish = error_check(vg.vgFinish)

################ 5.2 ################

# void vgSetf(VGParamType paramType, VGfloat value)
vg.vgSetf.argtypes = (enum, c_float)
vg.vgSetf.restype = None
# Errors: IllegalArgumentError
vgSetf = error_check(vg.vgSetf)

# void vgSeti(VGParamType paramType, VGint value)
vg.vgSeti.argtypes = (enum, c_int)
vg.vgSeti.restype = None
# Errors: IllegalArgumentError
vgSeti = error_check(vg.vgSeti)

# void vgSetfv(VGParamType paramType, VGint count, const VGfloat * values)
vg.vgSetfv.argtypes = (enum, c_int, float_p)
vg.vgSetfv.restype = None
# Errors: IllegalArgumentError
vgSetfv = error_check(vg.vgSetfv)

# void vgSetiv(VGParamType paramType, VGint count, const VGint * values)
vg.vgSetiv.argtypes = (enum, c_int, int_p)
vg.vgSetiv.restype = None
# Errors: IllegalArgumentError
vgSetiv = error_check(vg.vgSetiv)

# VGfloat vgGetf(VGParamType paramType)
vg.vgGetf.argtypes = (enum,)
vg.vgGetf.restype = c_float
# Errors: IllegalArgumentError
vgGetf = error_check(vg.vgGetf)

# VGint vgGeti(VGParamType paramType)
vg.vgGeti.argtypes = (enum,)
vg.vgGeti.restype = c_int
# Errors: IllegalArgumentError
vgGeti = error_check(vg.vgGeti)

# VGint vgGetVectorSize(VGParamType paramType)
vg.vgGetVectorSize.argtypes = (enum,)
vg.vgGetVectorSize.restype = c_int
# Errors: IllegalArgumentError
vgGetVectorSize = error_check(vg.vgGetVectorSize)

# void vgGetfv(VGParamType paramType, VGint count, VGfloat * values)
vg.vgGetfv.argtypes = (enum, c_int, float_p)
vg.vgGetfv.restype = None
# Errors: IllegalArgumentError
vgGetfv = error_check(vg.vgGetfv)

# void vgGetiv(VGParamType paramType, VGint count, VGint * values)
vg.vgGetiv.argtypes = (enum, c_int, int_p)
vg.vgGetiv.restype = None
# Errors: IllegalArgumentError
vgGetiv = error_check(vg.vgGetiv)

################ 5.3 ################

# void vgSetParameterf (VGHandle object, VGint paramType, VGfloat value)
vg.vgSetParameterf.argtypes = (vhandle, c_int, c_float)
vg.vgSetParameterf.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetParameterf = error_check(vg.vgSetParameterf)

# void vgSetParameteri (VGHandle object, VGint paramType, VGint value)
vg.vgSetParameteri.argtypes = (vhandle, c_int, c_int)
vg.vgSetParameteri.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetParameteri = error_check(vg.vgSetParameteri)

# void vgSetParameterfv(VGHandle object, VGint paramType, VGint count,
#                       const VGfloat * values)
vg.vgSetParameterfv.argtypes = (vhandle, c_int, c_int, float_p)
vg.vgSetParameterfv.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetParameterfv = error_check(vg.vgSetParameterfv)

# void vgSetParameteriv(VGHandle object, VGint paramType, VGint count,
#                       const VGint * values)
vg.vgSetParameteriv.argtypes = (vhandle, c_int, c_int, int_p)
vg.vgSetParameteriv.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetParameteriv = error_check(vg.vgSetParameteriv)

# VGfloat vgGetParameterf (VGHandle object, VGint paramType)
vg.vgGetParameterf.argtypes = (vhandle, c_int)
vg.vgGetParameterf.restype = c_float
# Errors: BadHandleError, IllegalArgumentError
vgGetParameterf = error_check(vg.vgGetParameterf)

# VGint vgGetParameteri (VGHandle object, VGint paramType)
vg.vgGetParameteri.argtypes = (vhandle, c_int)
vg.vgGetParameteri.restype = c_int
# Errors: BadHandleError, IllegalArgumentError
vgGetParameteri = error_check(vg.vgGetParameteri)

# VGint vgGetParameterVectorSize (VGHandle object, VGint paramType)
vg.vgGetParameterVectorSize.argtypes = (vhandle, c_int)
vg.vgGetParameterVectorSize.restype = c_int
# Errors: BadHandleError, IllegalArgumentError
vgGetParameterVectorSize = error_check(vg.vgGetParameterVectorSize)

# void vgGetParameterfv(VGHandle object, VGint paramType, VGint count,
#                       VGfloat * values)
vg.vgGetParameterfv.argtypes = (vhandle, c_int, c_int, float_p)
vg.vgGetParameterfv.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgGetParameterfv = error_check(vg.vgGetParameterfv)

# void vgGetParameteriv(VGHandle object, VGint paramType, VGint count,
#                       VGint * values)
vg.vgGetParameteriv.argtypes = (vhandle, c_int, c_int, int_p)
vg.vgGetParameteriv.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgGetParameteriv = error_check(vg.vgGetParameteriv)

################ 6.6 ################

# void vgLoadIdentity(void)
vg.vgLoadIdentity.argtypes = ()
vg.vgLoadIdentity.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgLoadIdentity = error_check(vg.vgLoadIdentity)

# void vgLoadMatrix(const VGfloat * m)
vg.vgLoadMatrix.argtypes = (float_p,)
vg.vgLoadMatrix.restype = None
# Errors: IllegalArgumentError
vgLoadMatrix = error_check(vg.vgLoadMatrix)

# void vgGetMatrix(VGfloat * m)
vg.vgGetMatrix.argtypes = (float_p,)
vg.vgGetMatrix.restype = None
# Errors: IllegalArgumentError
vgGetMatrix = error_check(vg.vgGetMatrix)

# void vgMultMatrix(const VGfloat * m)
vg.vgMultMatrix.argtypes = (float_p,)
vg.vgMultMatrix.restype = None
# Errors: IllegalArgumentError
vgMultMatrix = error_check(vg.vgMultMatrix)

# void vgTranslate(VGfloat tx, VGfloat ty)
vg.vgTranslate.argtypes = (c_float, c_float)
vg.vgTranslate.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgTranslate = error_check(vg.vgTranslate)

# void vgScale(VGfloat sx, VGfloat sy)
vg.vgScale.argtypes = (c_float, c_float)
vg.vgScale.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgScale = error_check(vg.vgScale)

# void vgShear(VGfloat shx, VGfloat shy)
vg.vgShear.argtypes = (c_float, c_float)
vg.vgShear.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgShear = error_check(vg.vgShear)

# void vgRotate(VGfloat angle)
vg.vgRotate.argtypes = (c_float,)
vg.vgRotate.restype = None
# TODO: Remove error_check? The spec indicates no errors for this function.
vgRotate = error_check(vg.vgRotate)

################ 7.2 ################

# void vgMask(VGHandle mask, VGMaskOperation operation, VGint x, VGint y,
#             VGint width, VGint height)
vg.vgMask.argtypes = (vhandle, enum, c_int, c_int, c_int, c_int)
vg.vgMask.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgMask = error_check(vg.vgMask)

# void vgRenderToMask(VGPath path, VGbitfield paintModes,
#                     VGMaskOperation operation)
vg.vgRenderToMask.argtypes = (vhandle, bitfield, enum)
vg.vgRenderToMask.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgRenderToMask = error_check(vg.vgRenderToMask)

# VGMaskLayer vgCreateMaskLayer(VGint width, VGint height)
vg.vgCreateMaskLayer.argtypes = (c_int, c_int)
vg.vgCreateMaskLayer.restype = vhandle
# Errors: IllegalArgumentError
vgCreateMaskLayer = error_check(vg.vgCreateMaskLayer)

# void vgDestroyMaskLayer(VGMaskLayer maskLayer)
vg.vgDestroyMaskLayer.argtypes = (vhandle,)
vg.vgDestroyMaskLayer.restype = None
# Errors: BadHandleError
vgDestroyMaskLayer = error_check(vg.vgDestroyMaskLayer)

# void vgFillMaskLayer(VGMaskLayer maskLayer, VGint x, VGint y,
#                      VGint width, VGint height, VGfloat value)
vg.vgFillMaskLayer.argtypes = (vhandle, c_int, c_int, c_int, c_int, c_float)
vg.vgFillMaskLayer.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgFillMaskLayer = error_check(vg.vgFillMaskLayer)

# void vgCopyMask(VGMaskLayer maskLayer, VGint dx, VGint dy,
#                 VGint sx, VGint sy, VGint width, VGint height)
vg.vgCopyMask.argtypes = (vhandle, c_int, c_int, c_int, c_int, c_int, c_int)
vg.vgCopyMask.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgCopyMask = error_check(vg.vgCopyMask)

################ 7.3 ################

# void vgClear(VGint x, VGint y, VGint width, VGint height)
vg.vgClear.argtypes = (c_int, c_int, c_int, c_int)
vg.vgClear.restype = None
# Errors: IllegalArgumentError
vgClear = error_check(vg.vgClear)

############### 8.6.2 ###############

# VGPath vgCreatePath(VGint pathFormat, VGPathDatatype datatype,
#                     VGfloat scale, VGfloat bias, VGint segmentCapacityHint,
#                     VGint coordCapacityHint, VGbitfield capabilities)
vg.vgCreatePath.argtypes = (c_int, enum, c_float, c_float, c_int, c_int, bitfield)
vg.vgCreatePath.restype = vhandle
# Errors: UnsupportedPathFormatError, IllegalArgumentError
vgCreatePath = error_check(vg.vgCreatePath)

# void vgClearPath(VGPath path, VGbitfield capabilities)
vg.vgClearPath.argtypes = (vhandle, bitfield)
vg.vgClearPath.restype = None
# Errors: BadHandleError
vgClearPath = error_check(vg.vgClearPath)

# void vgDestroyPath(VGPath path)
vg.vgDestroyPath.argtypes = (vhandle,)
vg.vgDestroyPath.restype = None
# Errors: BadHandleError
vgDestroyPath = error_check(vg.vgDestroyPath)

############### 8.6.4 ###############

# VGbitfield vgGetPathCapabilities(VGPath path)
vg.vgGetPathCapabilities.argtypes = (vhandle,)
vg.vgGetPathCapabilities.restype = bitfield
# Errors: BadHandleError
vgGetPathCapabilities = error_check(vg.vgGetPathCapabilities)

# void vgRemovePathCapabilities(VGPath path, VGbitfield capabilities)
vg.vgRemovePathCapabilities.argtypes = (vhandle, bitfield)
vg.vgRemovePathCapabilities.restype = None
# Errors: BadHandleError
vgRemovePathCapabilities = error_check(vg.vgRemovePathCapabilities)

############### 8.6.5 ###############

# void vgAppendPath(VGPath dstPath, VGPath srcPath)
vg.vgAppendPath.argtypes = (vhandle, vhandle)
vg.vgAppendPath.restype = None
# Errors: BadHandleError, PathCapabilityError
vgAppendPath = error_check(vg.vgAppendPath)

############### 8.6.6 ###############

# void vgAppendPathData(VGPath dstPath, VGint numSegments,
#                       const VGubyte * pathSegments, const void * pathData)
vg.vgAppendPathData.argtypes = (vhandle, c_int, ubyte_p, c_void_p)
vg.vgAppendPathData.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgAppendPathData = error_check(vg.vgAppendPathData)

############### 8.6.7 ###############

# void vgModifyPathCoords(VGPath dstPath, VGint startIndex,
#                         VGint numSegments, const void * pathData)
vg.vgModifyPathCoords.argtypes = (vhandle, c_int, c_int, c_void_p)
vg.vgModifyPathCoords.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgModifyPathCoords = error_check(vg.vgModifyPathCoords)

############### 8.6.8 ###############

# void vgTransformPath(VGPath dstPath, VGPath srcPath)
vg.vgTransformPath.argtypes = (vhandle, vhandle)
vg.vgTransformPath.restype = None
# Errors: BadHandleError, PathCapabilityError
vgTransformPath = error_check(vg.vgTransformPath)

############### 8.6.9 ###############

# VGboolean vgInterpolatePath(VGPath dstPath, VGPath startPath,
#                             VGPath endPath, VGfloat amount)
vg.vgInterpolatePath.argtypes = (vhandle, vhandle, vhandle, c_float)
vg.vgInterpolatePath.restype = vbool
# Errors: BadHandleError, PathCapabilityError
vgInterpolatePath = error_check(vg.vgInterpolatePath)

############### 8.6.10 ##############

# VGfloat vgPathLength(VGPath path, VGint startSegment, VGint numSegments)
vg.vgPathLength.argtypes = (vhandle, c_int, c_int)
vg.vgPathLength.restype = c_float
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgPathLength = error_check(vg.vgPathLength)

############### 8.6.11 ##############

# void vgPointAlongPath(VGPath path, VGint startSegment, VGint numSegments,
#                       VGfloat distance, VGfloat * x, VGfloat * y,
#                       VGfloat * tangentX, VGfloat * tangentY)
vg.vgPointAlongPath.argtypes = (vhandle, c_int, c_int, c_float, float_p,
                                float_p, float_p, float_p)
vg.vgPointAlongPath.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgPointAlongPath = error_check(vg.vgPointAlongPath)

############### 8.6.12 ##############

# void vgPathBounds(VGPath path, VGfloat * minX, VGfloat * minY,
#                   VGfloat * width, VGfloat * height)
vg.vgPathBounds.argtypes = (vhandle, float_p, float_p, float_p, float_p)
vg.vgPathBounds.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgPathBounds = error_check(vg.vgPathBounds)

# void vgPathTransformedBounds(VGPath path, VGfloat * minX, VGfloat * minY,
#                              VGfloat * width, VGfloat * height)
vg.vgPathTransformedBounds.argtypes = (vhandle, float_p, float_p, float_p,
                                       float_p)
vg.vgPathTransformedBounds.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgPathTransformedBounds = error_check(vg.vgPathTransformedBounds)

################ 8.8 ################

# void vgDrawPath(VGPath path, VGbitfield paintModes)
vg.vgDrawPath.argtypes = (vhandle, bitfield)
vg.vgDrawPath.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgDrawPath = error_check(vg.vgDrawPath)

############### 9.1.1 ###############

# VGPaint vgCreatePaint(void)
vg.vgCreatePaint.argtypes = ()
vg.vgCreatePaint.restype = vhandle
# Errors: None but OutOfMemoryError
vgCreatePaint = error_check(vg.vgCreatePaint)

# void vgDestroyPaint(VGPaint paint)
vg.vgDestroyPaint.argtypes = (vhandle,)
vg.vgDestroyPaint.restype = None
# Errors: None but OutOfMemoryError
vgDestroyPaint = error_check(vg.vgDestroyPaint)

vg.vg.argtypes = ()
vg.vg.restype = None
# Errors: 
vg = error_check(vg.vg)
