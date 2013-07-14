#!/usr/bin/env python3

'''OpenVG path drawing and editing.'''

# Copyright © 2013 Tim Pederick.
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
from ctypes import c_float

# Local imports.
from . import native, OpenVGError
from .params import (PathFormats, PathDatatypes, PathCapabilities, PathParams,
                     param_convert)

# Segment commands.
PathSegments = namedtuple('SegmentCommands_tuple',
                          ('CLOSE_PATH', 'MOVE_TO', 'LINE_TO', 'HLINE_TO',
                           'VLINE_TO', 'QUAD_TO', 'CUBIC_TO', 'SQUAD_TO',
                           'SCUBIC_TO', 'SCCWARC_TO', 'SCWARC_TO',
                           'LCCWARC_TO', 'LCWARC_TO')
                          )(*range(13))

def SegmentCommand(segment_type, is_absolute=True):
    '''Get the OpenVG numeric value for a segment command.

    A segment command comprises the segment type number (from the
    PathSegments named tuple), left-shifted one bit and with the low bit
    set to 1 (if the segment coordinates are relative to the last path
    position) or 0 (if they are absolute).

    '''
    return 2 * segment_type + (0 if is_absolute else 1)


class Path:
    '''Represents an OpenVG path, the core drawing primitive.

    Instance attributes:
        capabilities -- The bitmask describing the operations that may
            be performed on this path.
        phandle -- The foreign object handle for this path.

    '''
    def __init__(self, path_format=PathParams.default('FORMAT'),
                 datatype=PathParams.default('DATATYPE'),
                 scale=PathParams.default('SCALE'),
                 bias=PathParams.default('BIAS'),
                 segment_capacity_hint=0, coord_capacity_hint=0,
                 capabilities=PathCapabilities(ALL=1)):
        self.capabilities = capabilities
        self.phandle = native.vgCreatePath(path_format, datatype, scale, bias,
                                           segment_capacity_hint,
                                           coord_capacity_hint, capabilities)

        # Check for problems that didn't raise exceptions.
        if self.phandle == native.INVALID_HANDLE:
            raise OpenVGError('path creation unexpectedly failed')

    def __del__(self):
        native.vgDestroyPath(self)

    def clear(self, capabilities=None):
        native.vgClearPath(self, capabilities if capabilities is not None else
                           self.capabilities)

    @property
    def _as_parameter_(self):
        '''Get the path reference for use by foreign functions.'''
        return self.phandle

    def _get_param(self, param):
        '''Get the value of a path parameter.

        All path parameters are read-only; some are set at path
        creation, while others are automatically updated as segments are
        added.

        Keyword arguments:
            param -- The identifier of the parameter requested.

        '''
        # If param is not a known parameter type, PathParams.details[param]
        # will raise a KeyError, which we allow to propagate upwards.
        get_fn = (native.vgGetParameterf
                  if PathParams.details[param].values is c_float else
                  native.vgGetParameteri)
        return param_convert(param, get_fn(self, param), PathParams)

    @property
    def path_format(self):
        return _get_param(PathParams.FORMAT)

    @property
    def datatype(self):
        return _get_param(PathParams.DATATYPE)

    @property
    def scale(self):
        return _get_param(PathParams.SCALE)

    @property
    def bias(self):
        return _get_param(PathParams.BIAS)

    @property
    def num_segments(self): # TODO: Doesn't seem very Pythonic.
        return _get_param(PathParams.NUM_SEGMENTS)

    @property
    def num_coords(self): # TODO: Ditto.
        return _get_param(PathParams.NUM_COORDS)
