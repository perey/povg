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
from ctypes import (CDLL, POINTER, c_byte, c_ubyte, c_short, c_int, c_uint,
                    c_float, c_void_p)

# Local imports.
from . import VGError, error_codes

# Native library import.
vg = ctypes.CDLL('libOpenVG.so.1') # TODO: Cross-platform loading.

# Type definitions.
vbool = enum = bitfield = vhandle = c_uint
float2 = c_float * 2
(c_ubyte_p, c_short_p, c_int_p, c_uint_p,
 c_float_p) = (POINTER(c_type) for c_type in (c_ubyte, c_short, c_int, c_uint,
                                              c_float))
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
vg.vgSetfv.argtypes = (enum, c_int, c_float_p)
vg.vgSetfv.restype = None
# Errors: IllegalArgumentError
vgSetfv = error_check(vg.vgSetfv)

# void vgSetiv(VGParamType paramType, VGint count, const VGint * values)
vg.vgSetiv.argtypes = (enum, c_int, c_int_p)
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
vg.vgGetfv.argtypes = (enum, c_int, c_float_p)
vg.vgGetfv.restype = None
# Errors: IllegalArgumentError
vgGetfv = error_check(vg.vgGetfv)

# void vgGetiv(VGParamType paramType, VGint count, VGint * values)
vg.vgGetiv.argtypes = (enum, c_int, c_int_p)
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
vg.vgSetParameterfv.argtypes = (vhandle, c_int, c_int, c_float_p)
vg.vgSetParameterfv.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetParameterfv = error_check(vg.vgSetParameterfv)

# void vgSetParameteriv(VGHandle object, VGint paramType, VGint count,
#                       const VGint * values)
vg.vgSetParameteriv.argtypes = (vhandle, c_int, c_int, c_int_p)
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
vg.vgGetParameterfv.argtypes = (vhandle, c_int, c_int, c_float_p)
vg.vgGetParameterfv.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgGetParameterfv = error_check(vg.vgGetParameterfv)

# void vgGetParameteriv(VGHandle object, VGint paramType, VGint count,
#                       VGint * values)
vg.vgGetParameteriv.argtypes = (vhandle, c_int, c_int, c_int_p)
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
vg.vgLoadMatrix.argtypes = (c_float_p,)
vg.vgLoadMatrix.restype = None
# Errors: IllegalArgumentError
vgLoadMatrix = error_check(vg.vgLoadMatrix)

# void vgGetMatrix(VGfloat * m)
vg.vgGetMatrix.argtypes = (c_float_p,)
vg.vgGetMatrix.restype = None
# Errors: IllegalArgumentError
vgGetMatrix = error_check(vg.vgGetMatrix)

# void vgMultMatrix(const VGfloat * m)
vg.vgMultMatrix.argtypes = (c_float_p,)
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
vg.vgAppendPathData.argtypes = (vhandle, c_int, c_ubyte_p, c_void_p)
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
vg.vgPointAlongPath.argtypes = (vhandle, c_int, c_int, c_float, c_float_p,
                                c_float_p, c_float_p, c_float_p)
vg.vgPointAlongPath.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgPointAlongPath = error_check(vg.vgPointAlongPath)

############### 8.6.12 ##############

# void vgPathBounds(VGPath path, VGfloat * minX, VGfloat * minY,
#                   VGfloat * width, VGfloat * height)
vg.vgPathBounds.argtypes = (vhandle, c_float_p, c_float_p, c_float_p,
                            c_float_p)
vg.vgPathBounds.restype = None
# Errors: BadHandleError, PathCapabilityError, IllegalArgumentError
vgPathBounds = error_check(vg.vgPathBounds)

# void vgPathTransformedBounds(VGPath path, VGfloat * minX, VGfloat * minY,
#                              VGfloat * width, VGfloat * height)
vg.vgPathTransformedBounds.argtypes = (vhandle, c_float_p, c_float_p, c_float_p,
                                       c_float_p)
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
# Errors: BadHandleError
vgDestroyPaint = error_check(vg.vgDestroyPaint)

############### 9.1.2 ###############

# void vgSetPaint(VGPaint paint, VGbitfield paintModes)
vg.vgSetPaint.argtypes = (vhandle, bitfield)
vg.vgSetPaint.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetPaint = error_check(vg.vgSetPaint)

# VGPaint vgGetPaint(VGPaintMode paintMode)
vg.vgGetPaint.argtypes = (enum,)
vg.vgGetPaint.restype = vhandle
# Errors: IllegalArgumentError
vgGetPaint = error_check(vg.vgGetPaint)

################ 9.2 ################

# void vgSetColor(VGPaint paint, VGuint rgba)
vg.vgSetColor.argtypes = (vhandle, c_uint)
vg.vgSetColor.restype = None
# Errors: BadHandleError
vgSetColor = error_check(vg.vgSetColor)

# VGuint vgGetColor(VGPaint paint)
vg.vgGetColor.argtypes = (vhandle,)
vg.vgGetColor.restype = c_uint
# Errors: BadHandleError
vgGetColor = error_check(vg.vgGetColor)

################ 9.4 ################

# void vgPaintPattern(VGPaint paint, VGImage pattern)
vg.vgPaintPattern.argtypes = (vhandle, vhandle)
vg.vgPaintPattern.restype = None
# Errors: BadHandleError, ImageInUseError
vgPaintPattern = error_check(vg.vgPaintPattern)

################ 10.3 ###############

# VGImage vgCreateImage(VGImageFormat format, VGint width, VGint height,
#                       VGbitfield allowedQuality)
vg.vgCreateImage.argtypes = (enum, c_int, c_int, bitfield)
vg.vgCreateImage.restype = vhandle
# Errors: UnsupportedImageFormatError, IllegalArgumentError
vgCreateImage = error_check(vg.vgCreateImage)

# void vgDestroyImage(VGImage image)
vg.vgDestroyImage.argtypes = (vhandle,)
vg.vgDestroyImage.restype = None
# Errors: BadHandleError
vgDestroyImage = error_check(vg.vgDestroyImage)

################ 10.5 ###############

# void vgClearImage(VGImage image, VGint x, VGint y, VGint width, VGint height)
vg.vgClearImage.argtypes = (vhandle, c_int, c_int, c_int, c_int)
vg.vgClearImage.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgClearImage = error_check(vg.vgClearImage)

# void vgImageSubData(VGImage image, const void * data, VGint dataStride,
#                     VGImageFormat dataFormat, VGint x, VGint y,
#                     VGint width, VGint height)
vg.vgImageSubData.argtypes = (vhandle, c_void_p, c_int, enum, c_int, c_int,
                              c_int, c_int)
vg.vgImageSubData.restype = None
# Errors: BadHandleError, ImageInUseError, UnsupportedImageFormatError,
#         IllegalArgumentError
vgImageSubData = error_check(vg.vgImageSubData)

# void vgGetImageSubData(VGImage image, void * data, VGint dataStride,
#                        VGImageFormat dataFormat, VGint x, VGint y,
#                        VGint width, VGint height)
vg.vgGetImageSubData.argtypes = (vhandle, c_void_p, c_int, enum, c_int, c_int,
                                 c_int, c_int)
vg.vgGetImageSubData.restype = None
# Errors: BadHandleError, ImageInUseError, UnsupportedImageFormatError,
#         IllegalArgumentError
vgGetImageSubData = error_check(vg.vgGetImageSubData)

################ 10.6 ###############

# VGImage vgChildImage(VGImage parent, VGint x, VGint y,
#                      VGint width, VGint height)
vg.vgChildImage.argtypes = (vhandle, c_int, c_int, c_int, c_int)
vg.vgChildImage.restype = vhandle
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgChildImage = error_check(vg.vgChildImage)

# VGImage vgGetParent(VGImage image)
vg.vgGetParent.argtypes = (vhandle,)
vg.vgGetParent.restype = vhandle
# Errors: BadHandleError, ImageInUseError
vgGetParent = error_check(vg.vgGetParent)

################ 10.7 ###############

# void vgCopyImage(VGImage dst, VGint dx, VGint dy, VGImage src,
#                  VGint sx, VGint sy, VGint width, VGint height,
#                  VGboolean dither)
vg.vgCopyImage.argtypes = (vhandle, c_int, c_int, vhandle, c_int, c_int, c_int,
                           c_int, vbool)
vg.vgCopyImage.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgCopyImage = error_check(vg.vgCopyImage)

################ 10.8 ###############

# void vgDrawImage(VGImage image)
vg.vgDrawImage.argtypes = (vhandle,)
vg.vgDrawImage.restype = None
# Errors: BadHandleError, ImageInUseError
vgDrawImage = error_check(vg.vgDrawImage)

############### 10.9.1 ##############

# void vgSetPixels(VGint dx, VGint dy, VGImage src, VGint sx, VGint sy,
#                  VGint width, VGint height)
vg.vgSetPixels.argtypes = (c_int, c_int, vhandle, c_int, c_int, c_int, c_int)
vg.vgSetPixels.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgSetPixels = error_check(vg.vgSetPixels)

# void vgWritePixels(const void * data, VGint dataStride,
#                    VGImageFormat dataFormat, VGint dx, VGint dy,
#                    VGint width, VGint height)
vg.vgWritePixels.argtypes = (c_void_p, c_int, enum, c_int, c_int, c_int, c_int)
vg.vgWritePixels.restype = None
# Errors: UnsupportedImageFormatError, IllegalArgumentError
vgWritePixels = error_check(vg.vgWritePixels)

############### 10.9.2 ##############

# void vgGetPixels(VGImage dst, VGint dx, VGint dy, VGint sx, VGint sy,
#                  VGint width, VGint height)
vg.vgGetPixels.argtypes = (vhandle, c_int, c_int, c_int, c_int, c_int, c_int)
vg.vgGetPixels.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgGetPixels = error_check(vg.vgGetPixels)

# void vgReadPixels(void * data, VGint dataStride, VGImageFormat dataFormat,
#                   VGint sx, VGint sy, VGint width, VGint height)
vg.vgReadPixels.argtypes = (c_void_p, c_int, enum, c_int, c_int, c_int, c_int)
vg.vgReadPixels.restype = None
# Errors: UnsupportedImageFormatError, IllegalArgumentError
vgReadPixels = error_check(vg.vgReadPixels)

############### 10.10 ###############

# void vgCopyPixels(VGint dx, VGint dy, VGint sx, VGint sy,
#                   VGint width, VGint height)
vg.vgCopyPixels.argtypes = (c_int, c_int, c_int, c_int, c_int, c_int)
vg.vgCopyPixels.restype = None
# Errors: IllegalArgumentError
vgCopyPixels = error_check(vg.vgCopyPixels)

############### 11.4.2 ##############

# VGFont vgCreateFont(VGint glyphCapacityHint)
vg.vgCreateFont.argtypes = (c_int,)
vg.vgCreateFont.restype = vhandle
# Errors: IllegalArgumentError
vgCreateFont = error_check(vg.vgCreateFont)

# void vgDestroyFont(VGFont font)
vg.vgDestroyFont.argtypes = (vhandle,)
vg.vgDestroyFont.restype = None
# Errors: BadHandleError
vgDestroyFont = error_check(vg.vgDestroyFont)

############### 11.4.4 ##############

# void vgSetGlyphToPath(VGFont font, VGuint glyphIndex, VGPath path,
#                       VGboolean isHinted, const VGfloat glyphOrigin[2],
#                       const VGfloat escapement[2])
vg.vgSetGlyphToPath.argtypes = (vhandle, c_uint, vhandle, vbool, float2,
                                float2)
vg.vgSetGlyphToPath.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgSetGlyphToPath = error_check(vg.vgSetGlyphToPath)

# void vgSetGlyphToImage(VGFont font, VGuint glyphIndex, VGImage image,
#                        const VGfloat glyphOrigin[2],
#                        const VGfloat escapement[2])
vg.vgSetGlyphToImage.argtypes = (vhandle, c_uint, vhandle, float2, float2)
vg.vgSetGlyphToImage.restype = None
# Errors: BadHandleError, IllegalArgumentError, ImageInUseError
vgSetGlyphToImage = error_check(vg.vgSetGlyphToImage)

# void vgClearGlyph(VGFont font, VGuint glyphIndex)
vg.vgClearGlyph.argtypes = (vhandle, c_uint)
vg.vgClearGlyph.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgClearGlyph = error_check(vg.vgClearGlyph)

################ 11.5 ###############

# void vgDrawGlyph(VGFont font, VGuint glyphIndex, VGbitfield paintModes,
#                  VGboolean allowAutoHinting)
vg.vgDrawGlyph.argtypes = (vhandle, c_uint, bitfield, vbool)
vg.vgDrawGlyph.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgDrawGlyph = error_check(vg.vgDrawGlyph)

# void vgDrawGlyphs(VGFont font, VGint glyphCount, const VGuint * glyphIndices,
#                   const VGfloat * adjustments_x,
#                   const VGfloat * adjustments_y, VGbitfield paintModes,
#                   VGboolean allowAutoHinting)
vg.vgDrawGlyphs.argtypes = (vhandle, c_int, c_uint_p, c_float_p, c_float_p,
                            bitfield, vbool)
vg.vgDrawGlyphs.restype = None
# Errors: BadHandleError, IllegalArgumentError
vgDrawGlyphs = error_check(vg.vgDrawGlyphs)

################ 12.3 ###############

# void vgColorMatrix(VGImage dst, VGImage src, const VGfloat * matrix)
vg.vgColorMatrix.argtypes = (vhandle, vhandle, c_float_p)
vg.vgColorMatrix.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgColorMatrix = error_check(vg.vgColorMatrix)

################ 12.4 ###############

# void vgConvolve(VGImage dst, VGImage src, VGint kernelWidth,
#                 VGint kernelHeight, VGint shiftX, VGint shiftY,
#                 const VGshort * kernel, VGfloat scale, VGfloat bias,
#                 VGTilingMode tilingMode)
vg.vgConvolve.argtypes = (vhandle, vhandle, c_int, c_int, c_int, c_int,
                          c_short_p, c_float, c_float, enum)
vg.vgConvolve.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgConvolve = error_check(vg.vgConvolve)

# void vgSeparableConvolve(VGImage dst, VGImage src, VGint kernelWidth,
#                          VGint kernelHeight, VGint shiftX, VGint shiftY,
#                          const VGshort * kernelX, const VGshort * kernelY,
#                          VGfloat scale, VGfloat bias,
#                          VGTilingMode tilingMode)
vg.vgSeparableConvolve.argtypes = (vhandle, vhandle, c_int, c_int, c_int,
                                   c_int, c_short_p, c_short_p, c_float,
                                   c_float, enum)
vg.vgSeparableConvolve.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgSeparableConvolve = error_check(vg.vgSeparableConvolve)

# void vgGaussianBlur(VGImage dst, VGImage src, VGfloat stdDeviationX,
#                     VGfloat stdDeviationY, VGTilingMode tilingMode)
vg.vgGaussianBlur.argtypes = (vhandle, vhandle, c_float, c_float, enum)
vg.vgGaussianBlur.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgGaussianBlur = error_check(vg.vgGaussianBlur)

################ 12.5 ###############

# void vgLookup(VGImage dst, VGImage src, const VGubyte * redLUT,
#               const VGubyte * greenLUT, const VGubyte * blueLUT,
#               const VGubyte * alphaLUT, VGboolean outputLinear,
#               VGboolean outputPremultiplied)
vg.vgLookup.argtypes = (vhandle, vhandle, c_ubyte_p, c_ubyte_p, c_ubyte_p,
                        c_ubyte_p, vbool, vbool)
vg.vgLookup.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgLookup = error_check(vg.vgLookup)

# void vgLookupSingle(VGImage dst, VGImage src, const VGuint * lookupTable,
#                     VGImageChannel sourceChannel, VGboolean outputLinear,
#                     VGboolean outputPremultiplied)
vg.vgLookupSingle.argtypes = (vhandle, vhandle, c_uint_p, enum, vbool, vbool)
vg.vgLookupSingle.restype = None
# Errors: BadHandleError, ImageInUseError, IllegalArgumentError
vgLookupSingle = error_check(vg.vgLookupSingle)

vg.vg.argtypes = ()
vg.vg.restype = None
# Errors: 
vg = error_check(vg.vg)
