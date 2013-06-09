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
# TODO: Don't rely on Pegl; or at least, provide access to OpenVG context
# without relying on any particular way of creating that context. It's a
# pretty rough fit anyway, extending pegl.context.Context like this; the
# OpenVG context is essentially a singleton (or rather, a borg).
import pegl.display
import pegl.config
import pegl.context
import pegl.attribs

# Local library imports.
from .native import (vgFlush, vgFinish, vgSeti, vgSetf, vgSetiv, vgSetfv,
                     vgGetVectorSize, vgGeti, vgGetf, vgGetiv, vgGetfv,
                     c_int_p, c_float_p)

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
MatrixMode = namedtuple('MatrixMode_tuple',
                        ('PATH_USER_TO_SURFACE', 'IMAGE_USER_TO_SURFACE',
                         'FILL_PAINT_TO_USER', 'STROKE_PAINT_TO_USER',
                         'GLYPH_USER_TO_SURFACE')
                        )(0x1400, 0x1401, 0x1402, 0x1403,
                          0x1404)
FillRule = namedtuple('FillRule_tuple',
                      ('EVEN_ODD', 'NON_ZERO')
                      )(0x1900, 0x1901)
ImageQuality = namedtuple('ImageQuality_tuple',
                          ('NON_ANTIALIASED', 'FASTER', 'BETTER')
                          )(1, 2, 4) # TODO: Bitmask values!
RenderingQuality = namedtuple('RenderQuality_tuple',
                              ('NON_ANTIALIASED', 'FASTER', 'BETTER')
                              )(0x1200, 0x1201, 0x1202)
BlendMode = namedtuple('BlendMode_tuple',
                       ('SRC', 'SRC_OVER', 'DST_OVER', 'SRC_IN', 'DST_IN',
                        'MULTIPLY', 'SCREEN', 'DARKEN', 'LIGHTEN', 'ADDITIVE')
                       )(0x2000, 0x2001, 0x2002, 0x2003, 0x2004,
                         0x2005, 0x2006, 0x2007, 0x2008, 0x2009)
ImageMode = namedtuple('ImageMode_tuple',
                       ('NORMAL', 'MULTIPLY', 'STENCIL')
                       )(0x1F00, 0x1F01, 0x1F02)
CapStyle = namedtuple('CapStyle_tuple',
                      ('BUTT', 'ROUND', 'SQUARE')
                      )(0x1700, 0x1701, 0x1702)
JoinStyle = namedtuple('JoinStyle_tuple',
                       ('MITER', 'ROUND', 'BEVEL')
                       )(0x1800, 0x1801, 0x1802)
FillRule = namedtuple('FillRule_tuple',
                      ('EVEN_ODD', 'NON_ZERO')
                      )(0x1900, 0x1901)
PixelLayout = namedtuple('PixelLayout_tuple',
                         ('UNKNOWN', 'RGB_VERTICAL', 'BGR_VERTICAL',
                          'RGB_HORIZONTAL', 'BGR_HORIZONTAL')
                         )(0x1300, 0x1301, 0x1302, 0x1303, 0x1304)

# Context parameter getter/setter factories.
# TODO: Factory style (perhaps only for _getset()) that is aware of named
# tuples being used for its legal values.
def _get_vector(param_id, type_=int, known_size=None):
    '''Dynamically create a getter function for a vector parameter.

    The functions thus created have all implementation details built in
    when created (somewhat like currying a function), and accept one
    argument, called self. They are thus suitable for use as getter
    methods for properties.

    Keyword arguments:
        param_id -- The integer value that is passed to the native
            function to identify the parameter in question.
        type_ -- The data type stored in this vector. OpenVG only
            directly allows integer or floating-point parameters. (It
            also has boolean parameters, represented by integers, but no
            parameter is currently defined as a vector of booleans.) If
            this argument is set to something other than float, OpenVG
            will provide an integer which will then be converted to the
            supplied type. If omitted, the default is int.
        known_size -- The fixed size of this vector, if it has one. If
            omitted or None, the vector will be dynamically sized each
            time it is read.

    '''
    # Get the native function and pointer type needed.
    getv_fn, c_pointer = ((vgGetfv, c_float_p) if type_ is float else
                          (vgGetiv, c_int_p))
    # Create a function that either returns the static size (if we know what
    # that is) or fetches the current size when called.
    sizer = ((lambda: known_size) if known_size is not None else
             (lambda: vgGetVectorSize(param_id)))

    # Construct the getter function, with the above details baked in.
    def getter(self):
        size = sizer()
        array = (c_pointer * size)()
        getv_fn(param_id, size, array)
        return tuple(type_(elem) for elem in array)

    return getter

def _set_vector(param_id, type_=int):
    '''Dynamically create a setter function for a vector parameter.

    The functions thus created have all implementation details built in
    when created (somewhat like currying a function), and accept two
    argument, called self and val. They are thus suitable for use as
    setter methods for properties.

    Keyword arguments:
        param_id -- The integer value that is passed to the native
            function to identify the parameter in question.
        type_ -- The data type stored in this vector. OpenVG only
            directly allows integer or floating-point parameters. (It
            also has boolean parameters, represented by integers, but no
            parameter is currently defined as a vector of booleans.) If
            this argument is set to something other than float, ctypes
            will convert the values to integers and call the native
            functions that handle integers.

    '''
    # Get the native function and pointer type needed.
    setv_fn, c_pointer = ((vgSetfv, c_float_p) if type_ is float else
                          (vgSetiv, c_int_p))

    # Construct the setter function, with the above details baked in.
    def setter(self, val):
        size = len(val)
        array = (c_pointer * size)(*val)
        setv_fn(param_id, size, array)

    return setter

def _get(param, name, values, type_=int):
    '''Create a read-only property with a scalar value.

    Keyword arguments:
        param -- A key from _params identifying the context parameter.
        name -- A human-readable name for the property.
        values -- A human-readable description of the values this
            property can have.
        type_ -- The type of this property. OpenVG only directly allows
            integer or floating-point parameters, although it also has
            boolean parameters represented by integers. If this argument
            is set to something other than float, OpenVG will provide an
            integer which will then be converted to the supplied type.
            If omitted, the default is int.

    '''
    param_id = _params[param]
    get_fn = (vgGetf if type_ is float else vgGeti)
    return property(fget=lambda self: type_(get_fn(param_id)),
                    doc=('The {} (read-only).\n\n'
                         '    Possible values are {}.\n'.format(name, values)))

def _getv(param, name, values, type_=int, known_size=None):
    '''Create a read-only property with a vector value.

    Keyword arguments:
        param -- A key from _params identifying the context parameter.
        name -- A human-readable name for the property.
        values -- A human-readable description of the values this
            property can have.
        type_ -- The data type stored in this vector. OpenVG only
            directly allows integer or floating-point parameters. (It
            also has boolean parameters, represented by integers, but no
            parameter is currently defined as a vector of booleans.) If
            this argument is set to something other than float, OpenVG
            will provide an integer which will then be converted to the
            supplied type. If omitted, the default is int.
        known_size -- The fixed size of this vector, if it has one. If
            omitted or None, the vector will be dynamically sized each
            time it is read.

    '''
    param_id = _params[param]
    return property(fget=_get_vector(param_id, type_, known_size),
                    doc=('The {} (read-only).\n\n'
                         '    Possible values are {}.\n'.format(name, values)))

def _getset(param, name, values, type_=int):
    '''Create a read/write property with a scalar value.

    Keyword arguments:
        param -- A key from _params identifying the context parameter.
        name -- A human-readable name for the property.
        values -- A human-readable description of the values this
            property can take.
        type_ -- The type of this property. OpenVG only directly allows
            integer or floating-point parameters, although it also has
            boolean parameters represented by integers. If this argument
            is set to something other than float, OpenVG will provide an
            integer which will then be converted to the supplied type.
            If omitted, the default is int.

    '''
    param_id = _params[param]
    (get_fn, set_fn, c_type) = ((vgGetf, vgSetf, c_float) if type_ is float
                                else (vgGeti, vgSeti, c_int))
    return property(fget=lambda self: type_(get_fn(param_id)),
                    fset=lambda self, val: set_fn(param_id, c_type(val)),
                    doc=('The {}.\n\n'
                         '    Legal values are {}.\n'.format(name, values)))

def _getsetv(param, name, values, type_=int, known_size=None):
    '''Create a read/write property with a vector value.'''
    param_id = _params[param]
    return property(fget=_get_vector(param_id, type_, known_size),
                    fset=_set_vector(param_id, type_),
                    doc=('The {}.\n\n'
                         '    Legal values are {}.\n'.format(name, values)))

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

    @staticmethod
    def flush():
        '''Force operations on the current context to finish.

        Calling this function will ensure that any outstanding operations
        will finish in finite time, but it will not block while waiting
        for completion of those operations.

        '''
        vgFlush()

    @staticmethod
    def finish():
        '''Force operations on the current context to finish.

        When called, this function will not return until all outstanding
        operations are complete.

        '''
        vgFinish()

    matrix_mode = _getset('MATRIX_MODE', 'transform matrix mode',
                          'contained in the MatrixMode named tuple')
    fill_rule = _getset('FILL_RULE', 'path fill rule',
                        'contained in the FillRule named tuple')
    image_quality = _getset('IMAGE_QUALITY', '',
                            'contained in the ImageQuality named tuple')
    rendering_quality = _getset('RENDERING_QUALITY', '', #TODO
                                'contained in the RenderingQuality named tuple')
    blend_mode = _getset('BLEND_MODE', '', #TODO
                         'contained in the BlendMode named tuple')
    image_mode = _getset('IMAGE_MODE', '', #TODO
                         'contained in the ImageMode named tuple')
    scissor_rects = _getsetv('SCISSOR_RECTS', '', #TODO
                             # TODO: Flatten the tuple of 4-tuples! This needs
                             # some special handling to be written into either
                             # _getsetv or _set_vector (not sure which). And
                             # I should probably unflatten them on read, too.
                             '4-tuples of (x, y, width, height) for each '
                             'scissoring rectangle')
    # TODO: One property for both of these.
    color_transform = _getset('COLOR_TRANSFORM', '', #TODO
                              'booleans', type_=bool)
    color_transform_values = _getsetv('COLOR_TRANSFORM_VALUES', '', #TODO
                                      'eight color components (red, green, '
                                      'blue, alpha for XX and YY)',
                                      type_=float, known_size=8)
    # TODO: One property for all stroke parameters.
    stroke_line_width = _getset('STROKE_LINE_WIDTH', '', #TODO
                                'non-negative floats', type_=float)
    stroke_cap_style = _getset('STROKE_CAP_STYLE', '', #TODO
                               'contained in the CapStyle named tuple')
    stroke_join_style = _getset('STROKE_JOIN_STYLE', '', #TODO
                                'contained in the JoinStyle named tuple')
    stroke_miter_limit = _getset('STROKE_MITER_LIMIT', '', #TODO
                                 'non-negative floats', type_=float)

    max_kernel_size = _get('MAX_KERNEL_SIZE', 'maximum kernel size',
                           'positive integers')
