#!/usr/bin/env python3

'''OpenVG context access.

This module depends on Pegl, a Python wrapper around the EGL library. If
you are using Povg with some other means of managing contexts, you
should not import this module. Other Povg modules will not import this
module themselves.

'''
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

# Standard library imports.
from collections import namedtuple
from ctypes import c_float, c_int

# Pegl library imports.
import pegl.display
import pegl.config
import pegl.context
import pegl.attribs

# Local library imports.
from .native import (vgFlush, vgFinish, vgSeti, vgSetf, vgSetiv, vgSetfv,
                     vgGetVectorSize, vgGeti, vgGetf, vgGetiv, vgGetfv)

# Context parameter types.
_params = {
    # Mode settings
    'MATRIX_MODE': 0x1100,
    'FILL_RULE': 0x1101,
    'IMAGE_QUALITY': 0x1102,
    'RENDERING_QUALITY': 0x1103,
    'BLEND_MODE': 0x1104,
    'IMAGE_MODE': 0x1105,

    # Scissoring rectangles
    'SCISSOR_RECTS': 0x1106,

    # Colour transformation
    'COLOR_TRANSFORM': 0x1170,
    'COLOR_TRANSFORM_VALUES': 0x1171,

    # Stroke parameters
    'STROKE_LINE_WIDTH': 0x1110,
    'STROKE_CAP_STYLE': 0x1111,
    'STROKE_JOIN_STYLE': 0x1112,
    'STROKE_MITER_LIMIT': 0x1113,
    'STROKE_DASH_PATTERN': 0x1114,
    'STROKE_DASH_PHASE': 0x1115,
    'STROKE_DASH_PHASE_RESET': 0x1116,

    # Tiling edge fill colour
    'TILE_FILL_COLOR': 0x1120,

    # Clear colour
    'CLEAR_COLOR': 0x1121,

    # Glyph origin
    'GLYPH_ORIGIN': 0x1122,

    # Alpha masking and scissoring
    'MASKING': 0x1130,
    'SCISSORING': 0x1131,

    # Pixel layout information
    'PIXEL_LAYOUT': 0x1140,
    'SCREEN_LAYOUT': 0x1141,

    # Filter source format selection
    'FILTER_FORMAT_LINEAR': 0x1150,
    'FILTER_FORMAT_PREMULTIPLIED': 0x1151,

    # Filter destination write enable mask
    'FILTER_CHANNEL_MASK': 0x1152,

    # Read-only implementation limits
    'MAX_SCISSOR_RECTS': 0x1160,
    'MAX_DASH_COUNT': 0x1161,
    'MAX_KERNEL_SIZE': 0x1162,
    'MAX_SEPARABLE_KERNEL_SIZE': 0x1163,
    'MAX_COLOR_RAMP_STOPS': 0x1164,
    'MAX_IMAGE_WIDTH': 0x1165,
    'MAX_IMAGE_HEIGHT': 0x1166,
    'MAX_IMAGE_PIXELS': 0x1167,
    'MAX_IMAGE_BYTES': 0x1168,
    'MAX_FLOAT': 0x1169,
    'MAX_GAUSSIAN_STD_DEVIATION': 0x116A}

# Context parameter values.
MatrixMode = namedtuple('MatrixMode',
                        ('path_u2s', 'image_u2s', 'fill_p2u', 'stroke_p2u',
                         'glyph_u2s')
                        )(0x1400, 0x1401, 0x1402, 0x1403,
                          0x1404)
FillRule = namedtuple('FillRule',
                      ('even_odd', 'non_zero')
                      )(0x1900, 0x1901)
ImageQuality = namedtuple('ImageQuality',
                          ('no_aa', 'faster', 'better')
                          )(1, 2, 4)
RenderQuality = namedtuple('RenderQuality',
                           ('no_aa', 'faster', 'better')
                           )(0x1200, 0x1201, 0x1202)
BlendMode = namedtuple('BlendMode',
                       ('src', 'src_over', 'dst_over', 'src_in', 'dst_in',
                        'multiply', 'screen', 'darken', 'lighten', 'additive')
                       )(0x2000, 0x2001, 0x2002, 0x2003, 0x2004,
                         0x2005, 0x2006, 0x2007, 0x2008, 0x2009)
ImageMode = namedtuple('ImageMode',
                       ('normal', 'multiply', 'stencil')
                       )(0x1F00, 0x1F01, 0x1F02)
ScissorRects = namedtuple('ScissorRects',
                          ('normal', 'multiply', 'stencil')
                          )(0x1F00, 0x1F01, 0x1F02)

# Context parameter getter/setter factories.
def _get(param, name, values, type_=int):
    '''Create a read-only property with a scalar value.

    Keyword arguments:
        param -- A key from _params identifying the context parameter.
        name -- A human-readable name for the property.
        values -- A human-readable description of the values this
            property can have.
        type_ -- The type of this property, either int or float. If
            omitted, the default is int.

    '''
    param_id = _params[param]
    get_fn = {int: vgGeti, float: vgGetf}[type_]
    return property(fget=lambda self: type_(get_fn(param_id)),
                    doc=('The {} (read-only).\n\n'
                         '    Possible values are {}.\n'.format(name, values)))

def _getv(param, type_=int):
    '''Create a read-only property with a vector value.'''
    pass

def _getset(param, name, values, type_=int):
    '''Create a read/write property with a scalar value.

    Keyword arguments:
        param -- A key from _params identifying the context parameter.
        name -- A human-readable name for the property.
        values -- A human-readable description of the values this
            property can take.
        type_ -- The type of this property, one of int, float or bool.
            If omitted, the default is int.

    '''
    param_id = _params[param]
    get_fn, set_fn, c_type = {int: (vgGeti, vgSeti, c_int),
                              bool: (vgGeti, vgSeti, c_int),
                              float: (vgGetf, vgSetf, c_float)}[type_]
    return property(fget=lambda self: type_(get_fn(param_id)),
                    fset=lambda self, val: set_fn(param_id, c_type(val)),
                    doc=('The {}.\n\n'
                         '    Legal values are {}.\n'.format(name, values)))

def _getsetv(param, name, values_tuple, type_=int):
    '''Create a read/write property with a vector value.'''
    pass

# The OpenVG context itself.
class Context(pegl.context.Context):
    '''Represents an EGL context configured for OpenVG.

    Instance attributes:
        display, config, ctxhandle, render_buffer -- Inherited from
            pegl.context.Context.
        api -- Inherited from pegl.context.Context. Should always be the
            string 'OpenVG'.
        api_version -- Inherited from pegl.context.Context, but never
            relevant.

    Access to OpenVG-specific context parameters is possible through
    the following attributes. Note that these parameters apply to the
    current context, not necessarily to the Context instance. You should
    ensure that this context instance is current before querying or
    setting any of these parameters.

    Context attributes:
        matrix_mode
        fill_rule
        image_quality
        rendering_quality
        blend_mode
        image_mode
        scissor_rects
        color_transform
        color_transform_values
        stroke_line_width
        stroke_cap_style
        stroke_join_style
        stroke_miter_limit
        stroke_dash_pattern
        stroke_dash_phase
        stroke_dash_phase_reset
        tile_fill_color
        clear_color
        glyph_origin
        masking
        scissoring
        screen_layout
        pixel_layout
        filter_format_linear
        filter_format_premultiplied
        filter_channel_mask

    Read-only context attributes:
        max_scissor_rects
        max_dash_count
        max_kernel_size
        max_separable_kernel_size
        max_gaussian_std_deviation
        max_color_ramp_stops
        max_image_width
        max_image_height
        max_image_pixels
        max_image_bytes
        max_float

    '''
    def __init__(self, display=None, config=None, share_context=None):
        '''Create the context.

        Keyword arguments:
            display -- As the instance attribute. If omitted, the
                current display is used.
            config -- As the instance attribute. If omitted, the first
                available OpenVG-supporting configuration will be used.
            share_context -- An optional OpenVG context with which this
                one will share state.

        '''
        if display is None:
            display = pegl.display.current_display()
        if config is None:
            openvg = pegl.attribs.config.ClientAPIs(OPENVG=1)
            config = pegl.config.get_configs(display,
                                             {'RENDERABLE_TYPE': openvg})[0]
        pegl.context.bind_api('OpenVG')
        super().__init__(display, config, share_context)

        assert self.api == 'OpenVG'

    matrix_mode = _getset('MATRIX_MODE', 'transform matrix mode',
                          'contained in the MatrixMode named tuple')
    fill_rule = _getset('FILL_RULE', 'path fill rule',
                        'contained in the FillRule named tuple')

    max_kernel_size = _get('MAX_KERNEL_SIZE', 'maximum kernel size',
                           'positive integers')
