#!/usr/bin/env python3

'''OpenVG 1.1 context access.'''

# Standard library imports.
import ctypes
from collections import namedtuple

# Local library imports.
from . import error_check, vg, vg_bool

# Parameter types.
_param = {
    # Mode settings
    'VG_MATRIX_MODE': 0x1100,
    'VG_FILL_RULE': 0x1101,
    'VG_IMAGE_QUALITY': 0x1102,
    'VG_RENDERING_QUALITY': 0x1103,
    'VG_BLEND_MODE': 0x1104,
    'VG_IMAGE_MODE': 0x1105,

    # Scissoring rectangles
    'VG_SCISSOR_RECTS': 0x1106,

    # Colour transformation
    'VG_COLOR_TRANSFORM': 0x1170,
    'VG_COLOR_TRANSFORM_VALUES': 0x1171,

    # Stroke parameters
    'VG_STROKE_LINE_WIDTH': 0x1110,
    'VG_STROKE_CAP_STYLE': 0x1111,
    'VG_STROKE_JOIN_STYLE': 0x1112,
    'VG_STROKE_MITER_LIMIT': 0x1113,
    'VG_STROKE_DASH_PATTERN': 0x1114,
    'VG_STROKE_DASH_PHASE': 0x1115,
    'VG_STROKE_DASH_PHASE_RESET': 0x1116,

    # Tiling edge fill colour
    'VG_TILE_FILL_COLOR': 0x1120,

    # Clear colour
    'VG_CLEAR_COLOR': 0x1121,

    # Glyph origin
    'VG_GLYPH_ORIGIN': 0x1122,

    # Alpha masking and scissoring
    'VG_MASKING': 0x1130,
    'VG_SCISSORING': 0x1131,

    # Pixel layout information
    'VG_PIXEL_LAYOUT': 0x1140,
    'VG_SCREEN_LAYOUT': 0x1141,

    # Filter source format selection
    'VG_FILTER_FORMAT_LINEAR': 0x1150,
    'VG_FILTER_FORMAT_PREMULTIPLIED': 0x1151,

    # Filter destination write enable mask
    'VG_FILTER_CHANNEL_MASK': 0x1152,

    # Read-only implementation limits
    'VG_MAX_SCISSOR_RECTS': 0x1160,
    'VG_MAX_DASH_COUNT': 0x1161,
    'VG_MAX_KERNEL_SIZE': 0x1162,
    'VG_MAX_SEPARABLE_KERNEL_SIZE': 0x1163,
    'VG_MAX_COLOR_RAMP_STOPS': 0x1164,
    'VG_MAX_IMAGE_WIDTH': 0x1165,
    'VG_MAX_IMAGE_HEIGHT': 0x1166,
    'VG_MAX_IMAGE_PIXELS': 0x1167,
    'VG_MAX_IMAGE_BYTES': 0x1168,
    'VG_MAX_FLOAT': 0x1169,
    'VG_MAX_GAUSSIAN_STD_DEVIATION': 0x116A}

# Parameter value enumerations.
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

def name_lookup(ntup, val):
    '''Get the name of a value from a named tuple.'''
    try:
        return [k for k, v in ntup.__dict__.items() if v == val][0]
    except IndexError:
        # Key does not exist.
        return None

# Getter/setter factories.
def _get(param, name, values, type_=int):
    '''Create a read-only parameter with a scalar value.'''
    by_type = {int: vg.vgGeti,
               float: vg.vgGetf}
    get_fn = by_type[type_]

    getter = error_check(lambda self: type_(get_fn(_param[param])))
    doc = ('The {} (read-only).\n\n'
           '    Possible values are {}.\n'.format(name, values))

    return property(getter, doc=doc)

def _getv(param, type_=int):
    '''Create a read-only parameter with a vector value.'''
    pass

def _getset(param, name, values, type_=int):
    '''Create a read/write parameter with a scalar value.'''
    by_type = {int: (vg.vgGeti, vg.vgSeti, ctypes.c_int),
               float: (vg.vgGetf, vg.vgSetf, ctypes.c_float)}
    get_fn, set_fn, c_type = by_type[type_]

    getter = error_check(lambda self: type_(get_fn(_param[param])))
    setter = error_check(lambda self, val: set_fn(_param[param], c_type(val)))
    doc = 'The {}.\n\n    Legal values are {}.\n'.format(name, values)
    return property(getter, setter, doc=doc)

def _getsetv(param, name, values_tuple, type_=int):
    '''Create a read/write parameter with a vector value.'''
    pass

# The context itself.
class Context:
    '''The OpenVG context.

    The context is a singleton-like object, in that all instances of
    this class will access the same context parameters. It is therefore
    not generally necessary or useful to create more than one instance
    at a time.

    '''
    matrix_mode = _getset('VG_MATRIX_MODE', 'transform matrix mode',
                          'contained in the MatrixMode named tuple')
    fill_rule = _getset('VG_FILL_RULE', 'path fill rule',
                          'contained in the FillRule named tuple')

    max_kernel_size = _get('VG_MAX_KERNEL_SIZE', 'maximum kernel size',
                           'positive integers')
