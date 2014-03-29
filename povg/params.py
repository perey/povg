#!/usr/bin/env python3

'''OpenVG parameter types.'''

# Copyright © 2013-14 Tim Pederick.
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
from ctypes import c_float, c_int

# Local imports.
from .native import (c_float_p, vgGetParameterf, vgGetParameterfv,
                     vgGetParameteri, vgGetParameteriv, vgSetParameterf,
                     vgSetParameterfv, vgSetParameteri, vgSetParameteriv)

# TODO: Unless the objects that are (almost) identical to their pegl.attribs
# counterparts are split out into a separate module that will serve both
# libraries, this module may well be too large and will have to be turned into
# a package like pegl.attribs. (If they ARE split out into a common module,
# then pegl.attribs will shrink and can probably be turned into a module!)

# Native type definitions.
c_float4 = c_float * 4
c_float5 = c_float * 5

# Named tuple for storing the details of a parameter field. Note that the
# "default" field might only contain the default for setting a parameter,
# not the default for an unset value, which may be implementation-defined.
Details = namedtuple('Details', ('desc', 'values', 'default'))

# Convenience functions for identifying the native function call to get or set
# a parameter.
# TODO: Save special-casing by using the vector functions for everything? It's
# completely allowable, as long as scalar types are passed with a count of 1.
# It's worth noting that most of the savings will be seen in other modules, not
# here--don't assume this was a bad idea because you think it won't change much
# in these two functions!
def native_getter(details):
    '''Identify the native function for getting a parameter.

    Keyword arguments:
        details -- An instance of the Details named tuple, describing
            the parameter to be fetched.

    '''
    if details.values is c_float:
        return vgGetParameterf
    else:
        # Is it a vector type?
        try:
            array_type = details.values._type_
        except AttributeError:
            # No, it's not.
            pass
        else:
            return (vgGetParameterfv if array_type is c_float else
                    vgGetParatemeriv)
    # Everything else is an integer (or handled as one, like booleans).
    return vgGetParameteri

def native_setter(details):
    '''Identify the native function for setting a parameter.

    Keyword arguments:
        details -- An instance of the Details named tuple, describing
            the parameter to be set.

    '''
    if details.values is c_float:
        return vgSetParameterf
    else:
        # Is it a vector type?
        try:
            array_type = details.values._type_
        except AttributeError:
            # No, it's not.
            pass
        else:
            return (vgSetParameterfv if array_type is c_float else
                    vgSetParatemeriv)
    # Everything else is an integer (or handled as one, like booleans).
    return vgSetParameteri

# Class for representing bit mask parameter types.
class BitMask:
    '''A bit mask with convenient Python representations.

    Class attributes:
        bit_names -- A sequence of names for the bits in the mask
            (least significant first). Any bits without names have
            None for the name. Each bit with a name in bit_names
            can also be accessed as an instance attribute with that
            name (assuming the name is a valid Python identifier).

    Instance attributes:
        bits -- The raw bits of the mask (least significant first).

    '''
    # TODO: Track any modifications to the pegl.attribs.BitMask class, or else
    # split that out into its own module that both libraries share. Note that
    # the ability to initialise all bits with the ALL kwarg has been added to
    # this class only... so far.
    bit_names = []
    extensions = []

    @classmethod
    def _make_property(cls, bit_number):
        '''Create a property to get and set a specified bit value.

        This is necessary because code like this doesn't work:
        >>> getter = lambda self: self.bits[bit_number]

        For some reason, probably to do with the scope of the variable
        bit_number, every function so defined ends up taking on the same
        value of bit_number (the value it last had).

        '''
        def getter(self):
            '''Get the value of the bit at position {}.'''.format(bit_number)
            return self.bits[bit_number]

        def setter(self, val):
            '''Set or unset the bit at position {}.'''.format(bit_number)
            self.bits[bit_number] = bool(val)

        return property(getter, setter)

    @classmethod
    def extend(cls, bit_number, bit_name, override=False):
        '''Extend the bit mask by assigning a new bit name.

        Keyword arguments:
            bit_number -- The bit number to assign the new name to,
                counting from 0 (the least significant bit).
            bit_name -- The name to assign to the new bit.
            override -- Whether or not the new name can replace an
                existing name (either a standard name or from an
                extension). If False (the default), only bits with names
                that are currently None, or bits that enlarge the bit
                mask, may be given new names.

        '''
        off_end = bit_number - len(cls.bit_names)
        if off_end < 0:
            # The bit number falls within the current bit mask length.
            if (override or cls.bit_names[bit_number] is None):
                # Okay to assign new name.
                cls.bit_names[bit_number] = bit_name
            else:
                raise TypeError('could not rename existing bit (use override '
                                'argument to force change)')
        else:
            # The bit number is off the end of the bit mask.
            cls.bit_names.extend([None] * off_end + [bit_name])
        cls.extensions.append(bit_name)

    def __init__(self, *args, **kwargs):
        '''Set up the bit mask.

        Positional arguments:
            Integer values to use in initialising the bit mask. Each
            value is used in turn, effectively being OR'd together
            to create the mask.

        Keyword arguments:
            Initial bit values by name. The boolean value of the
            argument sets the relevant bit, overriding anything set
            from positional arguments. A keyword argument of ALL=1 will
            set all (named) bits to 1, causing all other keyword and
            positional arguments to be ignored.

        '''
        # TODO: The "ALL" code is a bit ugly and repetitious. Should it just
        # change the default value here to True for all bits, not just all
        # named bits, and leave it at that?
        self.bits = [False] * len(self.bit_names)

        # Set up access to bits by name.
        for bit_number, posname in enumerate(self.bit_names):
            if posname is None:
                # Unnamed bit.
                continue
            bitprop = self._make_property(bit_number)
            setattr(self.__class__, posname, bitprop)
            # Do we set all bits?
            if 'ALL' in kwargs:
                bitprop.fset(self, kwargs['ALL'])

        # Did we set all bits?
        if 'ALL' in kwargs:
            return

        # Initialise values from positional arguments.
        for mask in args:
            self._from_int(mask)

        # Initialise values from keyword arguments.
        for bit_name in kwargs:
            # If the keyword is not a valid bit name, we allow the
            # resulting AttributeError to propagate upwards.
            setter = getattr(self.__class__, bit_name).fset
            setter(self, kwargs[bit_name])

    @property
    def _as_parameter_(self):
        '''Get the bit mask value for use by foreign functions.'''
        return int(self)

    @property
    def _flags_set(self):
        '''Get the set bits by name.'''
        return tuple(compress(self.bit_names, self.bits))

    def __int__(self):
        '''Convert the bits to the corresponding integer.'''
        return sum(2 ** i if bit else 0 for i, bit in enumerate(self.bits))

    def __str__(self):
        '''List the set bits by name, separated by commas.'''
        return ','.join(self._flags_set)

    def _from_int(self, mask):
        '''Set this bit mask from an integer mask value.

        Keyword arguments:
            mask -- The integer mask to use. Any bits in excess of
                this mask's width are ignored.

        '''
        pos = 0
        mask = int(mask)
        # Go bit by bit until we run out of bits in either mask.
        while mask > 0 and pos < len(self.bits):
            mask, bit = divmod(mask, 2)
            self.bits[pos] = bool(bit)
            pos += 1


class Params:
    '''A set of OpenVG parameters.

    Subclasses of this class define parameters for different OpenVG
    objects such as paths and images. All useful information is
    available in class attributes and class methods, so these classes do
    not need to be instantiated.

    Class attributes:
        details -- A mapping with the parameter's integer value as the
            key, and a Details named-tuple instance (with a text
            description, the parameter type, and its default value) as
            the value.
        extensions -- A mapping of extension parameters loaded on this
            class to their integer values. By default, this is empty.
        Additionally, symbolic constants for all the known parameters
        are available as class attributes. Their names are the same as
        in the OpenVG standard, except without the VG_{object}_ prefix
        (e.g. the VG_PATH_FORMAT parameter 

    '''
    # TODO: Track any modifications to the pegl.attribs.Attribs class.
    # Note that default() is not available on that class... yet. Its
    # value_or_name behaviour could probably be extended to desc().
    extensions = {}

    @classmethod
    def default(cls, value_or_name):
        '''Get the default value of a given parameter.

        Unlike with desc(), it is an error to pass an invalid parameter.

        Keyword arguments:
            value_or_name -- The string or value representing the
                desired parameter.

        '''
        # Convert a name into a value.
        try:
            value = cls.__getattr__(value_or_name)
        except AttributeError:
            value = value_or_name
        # Allow a KeyError to propagate upwards.
        return cls.details[value].default

    @classmethod
    def desc(cls, value):
        '''Get a textual description of a given parameter.

        This may also be used to test for the validity of a given
        parameter. If the return value is None, the value supplied does
        not map to any known parameter.

        Keyword arguments:
            value -- The value representing the desired parameter.

        '''
        details = cls.details.get(value)
        return (None if details is None else details.desc)

    @classmethod
    def extend(cls, attr_name, value, attr_type, default, desc=None):
        '''Load an extension parameter into this class.

        Keyword arguments:
            attr_name -- The name of the extension parameter.
            attr_value -- The integer constant that represents the
                extension parameter.
            attr_type -- The type of the values that may be assigned to
                this parameter.
            default -- The default that this parameter takes.
            desc -- An optional string describing the parameter.

        '''
        cls.extensions[attr_name] = value
        cls.details[value] = Details('An extension parameter'
                                     if desc is None else desc,
                                     attr_type, default)


def param_convert(param, value, params):
    '''Convert a retrieved parameter value to something meaningful.

    Keyword arguments:
        param -- The identifier of the parameter in question.
        value -- The raw value retrieved for the parameter.
        params -- The Params subclass to which this parameter belongs.

    '''
    details = params.details[param]
    # Booleans are easily converted.
    if details.values is bool:
        return bool(value)
    else:
        # Determine whether we're dealing with a bitmask or not.
        try:
            if issubclass(details.values, BitMask):
                # We are! Pass it to the BitMask subclass's constructor.
                return details.values(value)
        except TypeError:
            # TypeError is raised by issubclass() if details.values is not a
            # class, let alone a subclass of BitMask.
            pass

    # All other types, including all vector types, are returned as-is.
    return value

# Parameters for path objects.
PathFormats = namedtuple('PathFormats_tuple', ('STANDARD',))(0,)

PathDatatypes = namedtuple('PathDatatypes_tuple',
                           ('S_8', 'S_16', 'S_32', 'F')
                           )(*range(4))

class PathCapabilities(BitMask):
    '''A bit mask representing the operations that a path can accept.'''
    bit_names = ['APPEND_FROM', 'APPEND_TO', 'MODIFY', 'TRANSFORM_FROM',
                 'TRANSFORM_TO', 'INTERPOLATE_FROM', 'INTERPOLATE_TO',
                 'PATH_LENGTH', 'POINT_ALONG_PATH', 'TANGENT_ALONG_PATH',
                 'PATH_BOUNDS', 'PATH_TRANSFORMED_BOUNDS']


class PathParams(Params):
    '''The set of OpenVG parameters relevant to path objects.'''
    FORMAT, DATATYPE, SCALE, BIAS, NUM_SEGMENTS, NUM_COORDS = range(0x1600,
                                                                    0x1606)
    details = {FORMAT: Details('The command format of the path', PathFormats,
                               PathFormats.STANDARD),
               DATATYPE: Details('The data type used to store coordinates on '
                                 'this path', PathDataTypes,
                                 PathDataTypes.S_32),
               SCALE: Details('The scale factor applied to all coordinates on '
                              'this path', c_float, 1.0),
               BIAS: Details('The offset from zero applied to all coordinates '
                             'on this path', c_float, 0.0),
               NUM_SEGMENTS: Details('The number of segments that make up '
                                     'this path', c_int, 0),
               NUM_COORDS: Details('The total number of coordinates across '
                                   'all segments of this path', c_int, 0.0)}


# Parameters for paint objects.
PaintTypes = namedtuple('PaintType_tuple', ('COLOR', 'LINEAR_GRADIENT',
                                            'RADIAL_GRADIENT', 'PATTERN')
                        )(*range(0x1b00, 0x1b04))
SpreadModes = namedtuple('SpreadModes_tuple', ('PAD', 'REPEAT', 'REFLECT')
                         )(*range(0x1c00, 0x1c03))
TilingModes = namedtuple('TilingModes_tuple', ('FILL', 'PAD', 'REPEAT',
                                               'REFLECT')
                         )(*range(0x1d00, 0x1d04))


class PaintParams(Params):
    '''The set of OpenVG parameters relevant to paint objects.'''
    (TYPE, COLOR, COLOR_RAMP_SPREAD_MODE, COLOR_RAMP_SPREAD_STOPS,
     LINEAR_GRADIENT, RADIAL_GRADIENT, PATTERN_TILING_MODE,
     COLOR_RAMP_PREMULTIPLIED) = range(0x1a00, 0x1a08)
    details = {TYPE: Details('The type of paint to apply', PaintType,
                             PaintType.COLOR),
               COLOR: Details('The RGBA paint colour, if the paint type is '
                              'solid colour', c_float4, (0.0, 0.0, 0.0, 1.0)),
               COLOR_RAMP_SPREAD_MODE: Details('What to do after the end of '
                                               'the first colour ramp, if the '
                                               'paint type is linear or '
                                               'radial gradient',
                                               SpreadModes, SpreadModes.PAD),
               COLOR_RAMP_SPREAD_STOPS: Details('The flattened sequence of '
                                                '5-tuples that define the '
                                                'offset position and RGBA '
                                                'colour of each colour ramp '
                                                'stop', c_float_p,
                                                c_float_p(())),
               COLOR_RAMP_PREMULTIPLIED: Details('Whether or not the colour '
                                                 'ramp stops have been '
                                                 'premultiplied with alpha',
                                                 bool, True),
               LINEAR_GRADIENT: Details('The start and end points of the '
                                        'linear gradient function', c_float4,
                                        (0.0, 0.0, 1.0, 0.0)),
               RADIAL_GRADIENT: Details('The centre point, focus point, and '
                                        'radius of the radial gradient '
                                        'function', c_float5, ()),
               PATTERN_TILING_MODE: Details('The method for determining '
                                            'colours outside the source '
                                            'image, if the paint type is '
                                            'pattern', TilingModes,
                                            TilingModes.FILL)}


# Parameters for image objects.
ImageFormats = namedtuple('ImageFormats_tuple', ('sRGBX_8888', 'sRGBA_8888',
                                                 'sRGBA_8888_PRE',
                                                 'sRGB_565', 'sRGBA_5551',
                                                 'sRGBA_4444', 'sL_8',
                                                 'lRGBX_8888', 'lRGBA_8888',
                                                 'lRGBA_8888_PRE', 'lL_8',
                                                 'A_8', 'BW_1', 'A_1', 'A_4',

                                                 'sXRGB_8888', 'sARGB_8888',
                                                 'sARGB_8888_PRE',
                                                 'sARGB_5551', 'sARGB_4444',
                                                 'lXRGB_8888', 'lARGB_8888',
                                                 'lARGB_8888_PRE',

                                                 'sBGRX_8888', 'sBGRA_8888',
                                                 'sBGRA_8888_PRE',
                                                 'sBGR_565', 'sBGRA_5551',
                                                 'sBGRA_4444', 'lBGRX_8888',
                                                 'lBGRA_8888',
                                                 'lBGRA_8888_PRE',

                                                 'sXBGR_8888', 'sABGR_8888',
                                                 'sABGR_8888_PRE',
                                                 'sABGR_5551', 'sABGR_4444',
                                                 'lXBGR_8888', 'lABGR_8888',
                                                 'lABGR_8888_PRE')
                          )(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                            64, 65, 66, 68, 69, 71, 72, 73,
                            128, 129, 130, 131, 132, 133, 134, 135, 136, 137,
                            192, 193, 194, 196, 197, 199, 200, 201)
# TODO: Consider replacing this with a structured bit-format object, if you can
# create one that isn't so hideously overblown that it looks like it should be
# out stomping through Tokyo.


class ImageParams(Params):
    '''The set of OpenVG parameters relevant to image objects.'''
    FORMAT, WIDTH, HEIGHT = range(0x1e00, 0x1e03)
    details = {FORMAT: Details('The pixel format and colour space of this '
                               'image',ImageFormats, ImageFormats.sRGBA_8888)
               WIDTH: Details('The width of this image, in pixels', c_int, 0),
               HEIGHT: Details('The height of this image, in pixels', c_int, 0)
               }


# Parameters for font objects.
class FontParams(Params):
    '''The set of OpenVG parameters relevant to font objects.'''
    NUM_GLYPHS = 0x2f00
    details = {NUM_GLYPHS: Details('The number of glyphs defined in this font',
                                   c_int, 0)}
