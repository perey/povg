#!/usr/bin/env python3

'''OpenVG path drawing and editing.'''

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
from contextlib import contextmanager
from ctypes import c_float
from itertools import chain

# Local imports.
from . import native, OpenVGError
from .params import (PathFormats, PathDatatypes, PathCapabilities, PathParams,
                     param_convert)
from .paint import PaintModes, kwargs_to_modes

# Segment commands.
PathSegments = namedtuple('PathSegments_tuple',
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

    Keyword arguments:
        segment_type -- The type of segment. A value from the
            PathSegments named tuple.
        is_absolute -- Whether or not this command is using absolute
            instead of relative coordinates. Defaults to true.

    '''
    # TODO: Accept segment type by name.
    return 2 * segment_type + (0 if is_absolute else 1)

# The centrepiece of the module, the big massive Path class itself.
class Path:
    '''Represents an OpenVG path, the core drawing primitive.

    Instance attributes:
        path_format -- The command format of the path. A value from the
            PathFormats named tuple.
        datatype -- The data type used to store coordinates on this
            path. A value from the PathDataTypes named tuple.
        scale, bias -- The scale factor and offset from zero applied to
            all coordinates on this path. The scale must be greater than
            zero, while bias is unrestricted.
        num_segments, num_coords -- The number of path segments that
            make up this path, and the number of individual coordinates
            (not coordinate pairs) that describe them.
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
        '''Initialise the OpenVG path.

        Keyword arguments:
            path_format, datatype, scale, bias -- As the instance
                attributes.
            segment_capacity_hint, coord_capacity_hint -- Optional hints
                for the number of segments and coordinates that this path
                should be expected to hold.
            capabilities -- As the instance attribute.

        '''
        # Set up state for the segment-queuing context manager.
        self._queuing = False
        self._queued_commands, self._queued_data = [], []

        # Store initial settings that can't be queried from OpenVG.
        self.segment_capacity_hint = segment_capacity_hint
        self.coord_capacity_hint = coord_capacity_hint

        # Create the OpenVG native object.
        self.phandle = native.vgCreatePath(path_format, datatype, scale, bias,
                                           segment_capacity_hint,
                                           coord_capacity_hint, capabilities)

        # Check for problems that didn't raise exceptions.
        if self.phandle == native.INVALID_HANDLE:
            raise OpenVGError('path creation unexpectedly failed')

    def __del__(self):
        '''Call the native OpenVG cleanup function.'''
        native.vgDestroyPath(self)

    def __iadd__(self, path):
        '''Use in-place addition to append another path to this one.'''
        self.append(path)

    def __len__(self):
        '''Get the length of this path, being its number of segments.'''
        return self.num_segments

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
        '''Get the actual path format reported by OpenVG.'''
        return _get_param(PathParams.FORMAT)

    @property
    def datatype(self):
        '''Get the actual coordinate data type reported by OpenVG.'''
        return _get_param(PathParams.DATATYPE)

    @property
    def scale(self):
        '''Get the scale value being used by OpenVG.'''
        return _get_param(PathParams.SCALE)

    @property
    def bias(self):
        '''Get the bias value being used by OpenVG.'''
        return _get_param(PathParams.BIAS)

    @property
    def num_segments(self): # TODO: Doesn't seem very Pythonic.
        '''Get the current number of segments in this path.

        This value is also reported as the length of this object by the
        len() function.

        '''
        return _get_param(PathParams.NUM_SEGMENTS)

    @property
    def num_coords(self): # TODO: Ditto.
        '''Get the current number of coordinates in this path.'''
        return _get_param(PathParams.NUM_COORDS)

    @property
    def capabilities(self):
        '''Get the current capabilities reported by OpenVG.'''
        return PathCapabilities(native.vgGetPathCapabilities(self))

    def _append_data(self, commands, data):
        '''Add new segment data to this path.

        This method should only be called by _add_segment() and by the
        queue_segments() context manager.

        Keyword arguments:
            commands -- A sequence containing the segment commands to
                append to the path.
            data -- A sequence containing the segment data for all
                commands.

        '''
        native.vgAppendPathData(self, len(commands), commands, data)

    def _add_segment(self, command, data):
        '''Prepare to add a new segment to this path.

        This method is called by each of the methods that add particular
        kinds of segments. If the path is currently in queuing mode
        (using the queue_segments() context manager), the segments are
        retained until the queuing mode is finished. Otherwise, the
        segments are appended immediately.

        Keyword arguments:
            command -- The command for the segment to add, as obtained
                from SegmentCommand.
            data -- A sequence containing the data for this segment.

        '''
        if self._queuing:
            self._queued_commands.append(command)
            self._queued_data.extend(data)
        else:
            self._append_data((command,), data)

    def append(self, path):
        '''Append all path segments from another path to this one.

        This is identical to using in-place addition on this path.

        '''
        native.vgAppendPath(path, self)

    def clear(self, capabilities=None):
        '''Clear all data from this path.

        According to the specification, clearing and reusing one path
        object may be more efficient than creating multiple short-lived
        paths.

        Keyword arguments:
            capabilities -- An optional new set of capabilities to apply
                to this path. If omitted, the previous capability set
                (as amended by remove_capabilities()) is reused.

        '''
        native.vgClearPath(self, capabilities if capabilities is not None else
                           self.capabilities)

    def remove_capabilities(self, *args, **kwargs):
        '''Remove the specified capabilities from this path.

        The OpenVG implementation may or may not honour this request,
        since path capabilities are only used for the sake of efficiency
        anyway.

        Keyword arguments:
            capabilities -- A PathCapabilities bit mask specifying the
                capabilities to be disabled.

        Alternatively, arguments (positional or keyword) can be passed
        in the same format as for the PathCapabilities constructor.

        '''
        try:
            capabilities = kwargs['capabilities']
        except KeyError:
            # No such keyword argument.
            capabilities = PathCapabilities(*args, **kwargs)
        native.vgRemovePathCapabilities(self, capabilities)

    def transform(self, to_path=None):
        '''Get the transformation of this path by the current matrix.

        An optional path (which may even be this path) can be supplied,
        in which case the transformed data is appended to that path. If
        no path is supplied, a new path with the transformed data is
        returned.

        '''
        dest = to_path or Path(self.path_format, self.datatype, self.scale,
                               self.bias, self.segment_capacity_hint,
                               self.coord_capacity_hint, self.capabilities)
        native.vgTransformPath(dest, self)
        if to_path is None:
            return dest

    @contextmanager
    def queue_segments(self):
        '''Queue up segment data, to be appended in a single operation.'''
        # TODO: Should be fairly easy to make this re-entrant: just save queue
        # state, do stuff, then restore state. But it means not using the
        # @contextmanager decorator any more...
        # http://docs.python.org/3/library/contextlib.html#reentrant-cms

        # Flag all data for enqueuing instead of immediate dispatch.
        self._queuing = True

        # Hand control to the with statement block.
        yield

        # Dispatch the queued data and empty the queues.
        self._append_data(self._queued_commands, self._queued_data)
        self._queued_commands, self._queued_data = [], []
        self._queuing = False

# TODO: Track the (sx, sy), (ox, oy) and (px, py) reference points.
# TODO: Use a named tuple for (x, y) pairs??
    def close_path(self):
        '''Append a close-path command to this path's segments.'''
        self._add_segment(SegmentCommand(PathSegments.CLOSE_PATH), ())

    def move_to(self, pos, is_absolute=True):
        '''Append a move-to command to this path's segments.

        Keyword arguments:
            pos -- The (x, y) coordinate pair of the point to move to.
            is_absolute -- Whether those coordinates are absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.MOVE_TO,
                                         is_absolute=is_absolute),
                          pos)

    def line_to(self, pos, is_absolute=True):
        '''Append a straight line to this path's segments.

        Keyword arguments:
            pos -- The (x, y) coordinate pair of the point to which the
                line is drawn.
            is_absolute -- Whether those coordinates are absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.LINE_TO,
                                         is_absolute=is_absolute),
                          pos)

    def hline_to(self, xpos, is_absolute=True):
        '''Append a horizontal line to this path's segments.

        Keyword arguments:
            xpos -- The x-coordinate of the point to which the line is
                drawn.
            is_absolute -- Whether that coordinate is absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.HLINE_TO,
                                         is_absolute=is_absolute),
                          (xpos,))

    def vline_to(self, ypos, is_absolute=True):
        '''Append a vertical line to this path's segments.

        Keyword arguments:
            ypos -- The y-coordinate of the point to which the line is
                drawn.
            is_absolute -- Whether that coordinate is absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.VLINE_TO,
                                         is_absolute=is_absolute),
                          (ypos,))

    def quad_to(self, ctrl, pos, is_absolute=True):
        '''Append a quadratic Bézier curve to this path's segments.

        Keyword arguments:
            ctrl -- The (x, y) coordinate pair of the control point for
                the Bézier curve.
            pos -- The (x, y) coordinate pair of the point to which the
                curve is drawn.
            is_absolute -- Whether those coordinates are absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.QUAD_TO,
                                         is_absolute=is_absolute),
                          chain(ctrl, pos))

    def cubic_to(self, ctrl0, ctrl1, pos, is_absolute=True):
        '''Append a cubic Bézier curve to this path's segments.

        Keyword arguments:
            ctrl0, ctrl1 -- The (x, y) coordinate pairs of the control
                points for the Bézier curve.
            pos -- The (x, y) coordinate pair of the point to which the
                curve is drawn.
            is_absolute -- Whether those coordinates are absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.CUBIC_TO,
                                         is_absolute=is_absolute),
                          chain(ctrl0, ctrl1, pos))

    def smooth_quad_to(self, pos, is_absolute=True):
        '''Append a quadratic Bézier curve to this path's segments.

        The control point for this curve is chosen such that the curve
        proceeds smoothly from the end of the previous segment.

        Keyword arguments:
            pos -- The (x, y) coordinate pair of the point to which the
                curve is drawn.
            is_absolute -- Whether those coordinates are absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.SQUAD_TO,
                                         is_absolute=is_absolute),
                          pos)

    def smooth_cubic_to(self, ctrl1, pos, is_absolute=True):
        '''Append a cubic Bézier curve to this path's segments.

        The first control point for this curve is chosen such that the
        curve proceeds smoothly from the end of the previous segment.

        Keyword arguments:
            pos -- The (x, y) coordinate pair of the point to which the
                curve is drawn.
            is_absolute -- Whether those coordinates are absolute (the
                default) or relative to the last path position.

        '''
        self._add_segment(SegmentCommand(PathSegments.SCUBIC_TO,
                                         is_absolute=is_absolute),
                          chain(ctrl1, pos))

    def arc_to(self, radii, rotation, pos, is_short=True, is_clockwise=False,
               is_absolute=True):
        '''Append an elliptical arc to this path's segments.

        The first control point for this curve is chosen such that the
        curve proceeds smoothly from the end of the previous segment.

        Keyword arguments:
            radii -- A single radius value (for a circular arc), or a
                pair of radius values, horizontal and then vertical.
            rotation -- The rotation angle of the arc, in degrees, given
                anticlockwise from the horizontal and vertical alignment
                of the above radii.
            pos -- The (x, y) coordinate pair of the point to which the
                arc is drawn.
            is_short -- Whether the arc is one of the two shorter
                arcs possible to the given point. Defaults to True.
            is_clockwise -- Whether the arc is one of the two clockwise
                arcs possible to the given point. Defaults to False.
            is_absolute -- Whether the coordinates in pos are absolute
                (the default) or relative to the last path position.

        '''
        # TODO: Conform to standard library (math) practice by using radians??
        # If I decide not to, povg.matrix will need to change to match.

        # Identify the appropriate arc command, out of the four candidates.
        command = {(False, False): PathSegments.LCCWARC_TO,
                   (False, True): PathSegments.LCWARC_TO,
                   (True, False): PathSegments.SCCWARC_TO,
                   (True, True): PathSegments.SCWARC_TO
                   }[(bool(is_short), bool(is_clockwise))]
        try:
            lrad = len(radii)
        except TypeError:
            # Doesn't have a len(); hopefully it's a single radius.
            radii = (float(radii),) * 2
        else:
            if lrad == 1:
                # One single radius, but in a sequence.
                radii = (radii[0],) * 2
            elif lrad != 2:
                # Huh?
                raise TypeError('expected 1 or 2 radii, got {}'.format(lrad))
            # Else two radii, just as expected.

        self._add_segment(SegmentCommand(command, is_absolute=is_absolute),
                          chain(radii, (rot,), pos))

    def modify_path(self, start, length, data):
        '''Modify existing path data for one or more segments.'''
        # TODO: This can surely be made more Pythonic and accessible?
        native.vgModifyPath(self, start, length, data)

    def interpolate(self, end, amount, to_path=None):
        '''Get an interpolation between this path and another.

        An optional path (which may even be this path) can be supplied,
        in which case the interpolated data is appended to that path. If
        no path is supplied, a new path with the interpolated data is
        returned.

        '''
        dest = to_path or Path(self.path_format, self.datatype, self.scale,
                               self.bias, self.segment_capacity_hint,
                               self.coord_capacity_hint, self.capabilities)
        native.vgInterpolatePath(dest, self, end, amount)
        if to_path is None:
            return dest

    def path_length(self, start=0, length=None):
        '''Get the (approximate) geometric length of this path.'''
        # Prep the parameters.
        if length is None:
            length = len(self)

        # Call the native function.
        pathlength = native.vgPathLength(self, start, length)

        # Check for errors that didn't cause an exception.
        if pathlength == -1:
            raise OpenVGError('path length operation unexpectedly failed')
        else:
            return pathlength

    def point_at(self, distance, start=0, length=None):
        '''Get the point some distance along this path.

        Note that if the path lacks the capabilities for querying either
        the coordinates or the tangent vector, no error will result. The
        returned values will simply be incorrect (all values should be
        0.0 in both tuples).

        Returns:
            A 2-tuple containing the coordinates of the point, as an
            (x, y) 2-tuple, and the tangent vector at the point, as
            an (i, j) 2-tuple.

        '''
        # TODO: Optional parameter to disable (or enable?) tangent or even
        # coordinate querying (by passing None instead of pointers).

        # Prep the parameters.
        if length is None:
            length = len(self)

        # Get pointers to hold the results.
        x, y, tx, ty = (native.make_float_p(), native.make_float_p(),
                        native.make_float_p(), native.make_float_p())

        # Call the native function.
        native.vgPointAlongPath(self, start, length, distance, x, y, tx, ty)

        # Dereference the pointers.
        return ((x.contents.value, y.contents.value),
                (tx.contents.value, ty.contents.value))

    def bounds(self, apply_transform=False):
        '''Get the bounding box of this path.'''
        # Get pointers to hold the results.
        x, y, width, height = (native.make_float_p(), native.make_float_p(),
                               native.make_float_p(), native.make_float_p())

        # Call the native function.
        (native.vgPathTransformedBounds if apply_transform else
         native.vgPathBounds)(self, x, y, width, height)

        # Dereference the pointers.
        return (x.contents.value, y.contents.value,
                width.contents.value, height.contents.value)

    def draw(self, fill=True, stroke=True):
        '''Draw the path.'''
        # Do we fill the path, stroke it, or both?
        mode = kwargs_to_modes(**kwargs)
        if mode == 0:
            return # TODO: Error?
        # Draw it!
        native.vgDrawPath(self, mode)

    def render_to_mask(self, mask_op, fill=True, stroke=True):
        '''Render this path to the current mask layer.'''
        # Do we fill the path, stroke it, or both?
        mode = kwargs_to_modes(**kwargs)
        if mode == 0:
            return # TODO: Error?
        # Do it!
        native.vgRenderToMask(self, mode, mask_op)
