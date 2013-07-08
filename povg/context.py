#!/usr/bin/env python3

'''OpenVG context access.

This module depends on Pegl, a Python wrapper around the EGL library. If
you are using Povg with some other means of managing contexts, you
should not import this module. Other Povg modules will not import this
module themselves.

'''
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
from . import flatten, unflatten
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

    # Alpha masking and scissoring
    'MASKING': 0x1130,
    'SCISSORING': 0x1131,
    'SCISSOR_RECTS': 0x1106,

    # Colour transformation
    'COLOR_TRANSFORM': 0x1170,
    'COLOR_TRANSFORM_VALUES': 0x1171,

    # Stroke parameters
    'STROKE_LINE_WIDTH': 0x1110,
    'STROKE_CAP_STYLE': 0x1111,
    'STROKE_JOIN_STYLE': 0x1112,
    'STROKE_MITER_LIMIT': 0x1113,

    # Stroke dash parameters
    'STROKE_DASH_PATTERN': 0x1114,
    'STROKE_DASH_PHASE': 0x1115,
    'STROKE_DASH_PHASE_RESET': 0x1116,

    # Fill and clear colours
    'TILE_FILL_COLOR': 0x1120,
    'CLEAR_COLOR': 0x1121,

    # Glyph origin
    'GLYPH_ORIGIN': 0x1122,

    # Pixel layout information
    'PIXEL_LAYOUT': 0x1140,
    'SCREEN_LAYOUT': 0x1141,

    # Filter settings
    'FILTER_FORMAT_LINEAR': 0x1150,
    'FILTER_FORMAT_PREMULTIPLIED': 0x1151,
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
def _get_vector(param_id, type_=int, flattened=False, known_size=None):
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
        flattened -- Whether or not the values are actually sequences of
            vectors that need to be "unflattened" after reading. The
            default is False; if True, known_size needs to be set.
        known_size -- The fixed size of this vector, if it has one. If
            omitted or None, the vector will be dynamically sized each
            time it is read. If flattened is True, the size applies to
            each vector in the sequence, not the sequence itself.

    '''
    # Get the native function and pointer type needed.
    getv_fn, c_pointer = ((vgGetfv, c_float_p) if type_ is float else
                          (vgGetiv, c_int_p))

    # Construct the getter function, with the above details baked in.
    if flattened:
        if known_size is None:
            raise TypeError('known_size must be supplied if flattened is True')

        def getter(self):
            size = vgGetVectorSize(param_id)
            array = (c_pointer * size)()
            getv_fn(param_id, size, array)
            return unflatten(type_(elem) for elem in array, known_size)
    else:
        # Create a function that either returns the static size (if we know
        # what that is) or fetches the current size when called.
        sizer = ((lambda: known_size) if known_size is not None else
                 (lambda: vgGetVectorSize(param_id)))

        def getter(self):
            size = sizer()
            array = (c_pointer * size)()
            getv_fn(param_id, size, array)
            return tuple(type_(elem) for elem in array)

    return getter

def _set_vector(param_id, type_=int, flattened=False, known_size=None):
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
        flattened -- Whether or not the values are actually sequences of
            vectors that need to be flattened before writing. The
            default is False.
        known_size -- The fixed size of this vector, if it has one. This
            parameter is ignored (and the actual len() of the value
            supplied is used) unless flattened is True, in which case
            the value applies to each vector in the sequence.

    '''
    # Get the native function and pointer type needed.
    setv_fn, c_pointer = ((vgSetfv, c_float_p) if type_ is float else
                          (vgSetiv, c_int_p))

    # Construct the setter function, with the above details baked in.
    if flattened:
        def setter(self, val):
            flat = flatten(val, known_size)
            size = len(flat)
            array = (c_pointer * size)(*flat)
            setv_fn(param_id, size, array)
    else:
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
            property can have. Ignored if type_ is bool.
        type_ -- The type of this property. OpenVG only directly allows
            integer or floating-point parameters, although it also has
            boolean parameters represented by integers. If this argument
            is set to something other than float, OpenVG will provide an
            integer which will then be converted to the supplied type.
            If omitted, the default is int.

    '''
    param_id = _params[param]
    get_fn = (vgGetf if type_ is float else vgGeti)

    docstring = ('Whether or not {} (read-only).\n'.format(name)
                 if type_ is bool else
                 'The {} (read-only).\n\n    Possible values are '
                 '{}.\n'.format(name, values))

    return property(fget=lambda self: type_(get_fn(param_id)),
                    doc=docstring)

def _getv(param, name, values, type_=int, flattened=False, known_size=None):
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
        flattened -- Whether or not the property is a sequence of
            vectors that needs to be "unflattened" after reading. If
            omitted, the default is False. If True, known_size must be
            specified.
        known_size -- The fixed size of this vector, if it has one. If
            omitted or None, the vector will be dynamically sized each
            time it is read. If flattened is True, this parameter is
            required, and specifies the size of each vector in the
            sequence, not of the sequence itself.

    '''
    param_id = _params[param]
    return property(fget=_get_vector(param_id, type_, flattened, known_size),
                    doc=('The {} (read-only).\n\n'
                         '    Possible values are {}.\n'.format(name, values)))

def _getset(param, name, values, type_=int, from_nt=None):
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
        from_nt -- An optional named tuple instance from which values
            must be drawn.

    '''
    # TODO: Do something useful with from_nt.
    param_id = _params[param]
    (get_fn, set_fn, c_type) = ((vgGetf, vgSetf, c_float) if type_ is float
                                else (vgGeti, vgSeti, c_int))

    docstring = ('Whether or not {}.\n'.format(name) if type_ is bool else
                 'The {}.\n\n    Legal values are {}.\n'.format(name, values))

    return property(fget=lambda self: type_(get_fn(param_id)),
                    fset=lambda self, val: set_fn(param_id, c_type(val)),
                    doc=docstring)

def _getsetv(param, name, values, type_=int, flattened=False, known_size=None):
    '''Create a read/write property with a vector value.

    Keyword arguments:
        param -- A key from _params identifying the context parameter.
        name -- A human-readable name for the property.
        values -- A human-readable description of the values this
            property can take.
        type_ -- The type of this property. OpenVG only directly allows
            integer or floating-point parameters. (It also has boolean
            parameters represented by integers, but currently no vectors
            of booleans). If this argument is set to something other
            than float, OpenVG will provide an integer which will then
            be converted to the supplied type. If omitted, the default
            is int.
        flattened -- Whether or not the property is a sequence of
            vectors that needs to be flattened on write and restored on
            read. If omitted, the default is False.
        known_size -- The known size of the vector values of this
            property. If omitted or None, the size will be checked on
            each read and write. If flattened is True, this parameter is
            required, and specifies the size of each vector in the
            sequence, not of the sequence itself.

    '''
    param_id = _params[param]
    return property(fget=_get_vector(param_id, type_, flattened, known_size),
                    fset=_set_vector(param_id, type_, flattened, known_size),
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

    # Mode settings
    matrix_mode = _getset('MATRIX_MODE', 'transform matrix mode',
                          'contained in the MatrixMode named tuple',
                          from_nt=MatrixMode)
    fill_rule = _getset('FILL_RULE', 'path fill rule',
                        'contained in the FillRule named tuple',
                        from_nt=FillRule)
    image_quality = _getset('IMAGE_QUALITY', 'image resampling quality',
                            'contained in the ImageQuality named tuple',
                            from_nt=ImageQuality)
    rendering_quality = _getset('RENDERING_QUALITY',
                                'overall rendering quality',
                                'contained in the RenderingQuality '
                                'named tuple', from_nt=RenderingQuality)
    blend_mode = _getset('BLEND_MODE', 'blending mode (from a subset of '
                         'Porter-Duff modes, plus some extras) to apply',
                         'contained in the BlendMode named tuple',
                         from_nt=BlendMode)
    image_mode = _getset('IMAGE_MODE', 'image drawing method',
                         'contained in the ImageMode named tuple',
                         from_nt=ImageMode)

    # Alpha masking and scissoring
    masking = _getset('MASKING', 'masking is active',
                      'booleans', type_=bool)
    scissoring = _getset('SCISSORING', 'scissoring is active',
                         'booleans', type_=bool)
    scissor_rects = _getsetv('SCISSOR_RECTS', 'scissoring rectangles, which '
                             'bound the drawing surface when scissoring is '
                             'enabled',
                             '4-tuples of (x, y, width, height) for each '
                             'scissoring rectangle',
                             flattened=True, known_size=4)

    # Colour transformation
    # TODO: One property for both of these.
    color_transform = _getset('COLOR_TRANSFORM',
                              'colour transformation is active',
                              'booleans', type_=bool)
    color_transform_values = _getsetv('COLOR_TRANSFORM_VALUES', 'parameters '
                                      'of the colour transformation',
                                      'eight color components (red, green, '
                                      'blue, alpha for scale and for bias)',
                                      type_=float, known_size=8)

    # Stroke parameters
    # TODO: One property for all stroke parameters.
    stroke_line_width = _getset('STROKE_LINE_WIDTH', 'width of the stroke',
                                'non-negative floats', type_=float)
    stroke_cap_style = _getset('STROKE_CAP_STYLE', 'style of the stroke ends',
                               'contained in the CapStyle named tuple',
                               from_nt=CapStyle)
    stroke_join_style = _getset('STROKE_JOIN_STYLE', 'style of stroke joins',
                                'contained in the JoinStyle named tuple',
                                from_nt=JoinStyle)
    stroke_miter_limit = _getset('STROKE_MITER_LIMIT', 'miter length limit, '
                                 'past which miter joins are converted to '
                                 'bevel joins',
                                 'non-negative floats', type_=float)

    # Stroke dash parameters
    # TODO: One property for all dash parameters.
    stroke_dash_pattern = _getsetv('STROKE_DASH_PATTERN', 'series of "on" '
                                   'and "off" lengths in the dash pattern',
                                   'sequences of even numbers of floats (an '
                                   'empty sequence disables dashes)',
                                   type_=float)
    stroke_dash_phase = _getset('STROKE_DASH_PHASE', 'offset before the dash '
                                'pattern begins', 'floats', type_=float)
    stroke_dash_phase_reset = _getset('STROKE_DASH_PHASE_RESET',
                                      'reset the dash pattern on each subpath',
                                      type_=bool)

    # Fill and clear colours
    tile_fill_color = _getsetv('TILE_FILL_COLOR', 'fill colour used for the '
                              'TILE_FILL tiling mode', '4-tuples of (R, G, B, '
                              'A) floats in the range [0, 1] (other values '
                               'will be clamped)', type_=float, known_size=4)
    clear_color = _getsetv('CLEAR_COLOR', 'colour used when fast-clearing '
                           'regions', '4-tuples of (R, G, B, A) floats in the '
                           'range [0, 1] (other values will be clamped)',
                           type_=float, known_size=4)

    # Glyph origin
    glyph_origin = _getsetv('GLYPH_ORIGIN', 'the current position of the '
                            'glyph "cursor"', '2-tuples of (x, y) floats',
                            type_=float, known_size=2)

    # Pixel layout information
    pixel_layout = _getset('PIXEL_LAYOUT', 'pixel geometry hint supplied to '
                           'the renderer', 'contained in the PixelLayout '
                           'named tuple', from_nt=PixelLayout)
    # This isn't specified as read-only, but the description implies it.
    screen_layout = _get('SCREEN_LAYOUT', 'pixel geometry of the current '
                         'display device', 'contained in the PixelLayout '
                         'named tuple', from_nt=PixelLayout)

    # Filter settings
    # TODO: One property for both filter source format conversions.
    filter_format_linear = _getset('FILTER_FORMAT_LINEAR', 'filter formats are '
                                   'converted to a linear colour space',
                                   'booleans', type_=bool)
    filter_format_premult = _getset('FILTER_FORMAT_PREMULTIPLIED', 'filter '
                                    'formats are converted to a premultiplied '
                                    'colour space', 'booleans', type_=bool)
    filter_channel_mask = _getset('FILTER_CHANNEL_MASK', 'colour channels of '
                                  'the filtered image to write', 'bitmasks of '
                                  'red, green, blue and alpha') # TODO: Bitmask!

    # Read-only implementation limits
    max_scissor_rects = _get('MAX_SCISSOR_RECTS', 'maximum number of '
                             'scissoring rectangles supported',
                             'positive integers (minimum 32)')
    max_dash_count = _get('MAX_DASH_COUNT', 'maximum number of dash segments '
                          'that may be specified',
                          'positive integers (minimum 16)')
    max_kernel_size = _get('MAX_KERNEL_SIZE', 'maximum kernel size (width '
                           'and/or height) for convolution',
                           'positive integers (minimum 7)')
    max_separable_kernel_size = _get('MAX_SEPARABLE_KERNEL_SIZE', 'maximum '
                                     'kernel size for separable convolution',
                                     'positive integers (minimum 15)')
    max_color_ramp_stops = _get('MAX_COLOR_RAMP_STOPS', 'maximum number of '
                                'gradient stops that may be specified',
                                'positive integers (minimum 32)')
    max_image_width = _get('MAX_IMAGE_WIDTH', 'maximum pixel width of images '
                           'and masks', 'positive integers (minimum 256)')
    max_image_height = _get('MAX_IMAGE_HEIGHT', 'maximum pixel height of '
                           'images and masks',
                            'positive integers (minimum 256)')
    max_image_pixels = _get('MAX_IMAGE_PIXELS', 'maximum number of pixels in '
                            'an image or mask',
                            'positive integers (minimum 65536)')
    max_image_bytes = _get('MAX_IMAGE_BYTES', 'maximum bytes of image data in '
                           'an image', 'positive integers (minimum 65536)')
    max_float = _get('MAX_FLOAT', 'largest floating-point number accepted by '
                     'this implementation', 'positive floating-point numbers '
                     '(minimum 1E+10)', type_=float)
    max_gaussian_std_deviation = _get('MAX_GAUSSIAN_STD_DEVIATION',
                                      'largest standard deviation accepted '
                                      'for Gaussian blur',
                                      'positive floating-point numbers '
                                      '(minimum 16.0)',
                                      type_=float)
