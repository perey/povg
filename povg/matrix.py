#!/usr/bin/env python3

'''OpenVG matrix transformations.

In OpenVG matrix operations, there is one "current" matrix on which all
operations are performed. Matrices can be read out and loaded in at
will, but only the last one loaded can be operated on. This module
abstracts away that restriction into a Matrix class.

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
from ctypes import c_float
from math import degrees

# Local imports.
from . import flatten, unflatten
from .native import (vgLoadIdentity, vgLoadMatrix, vgGetMatrix,
                     vgMultMatrix, vgTranslate, vgScale, vgShear, vgRotate)

# ctypes floating-point matrix type.
matrix_type = (c_float * 9)

class Matrix:
    '''Represents a 3×3 transform matrix.'''
    SIZE = 3
    def __init__(self, rows=None, from_current=False):
        '''Initialise this matrix.

        Keyword arguments:
            rows -- An optional 3-tuple of 3-tuples from which to
                populate this matrix.
            from_current -- Whether or not to populate this matrix from
                the current OpenVG matrix. Ignored if rows is not None.
                If rows is omitted and from_current is False (the
                default), the OpenVG matrix will be set to the identity
                matrix, and that will be copied into the new matrix.

        '''
        if rows is None:
            if not from_current:
                vgLoadIdentity()
            self._from_current()
        else:
            self.rows = rows
            assert (len(self.rows) == self.SIZE and
                    all(len(row) == self.SIZE for row in self.rows))

    def __repr__(self):
        return 'Matrix({!r})'.format(self.rows)

    def __contains__(self, val):
        return any(val in row for row in rows)

    def __getitem__(self, key):
        return self.rows[key]

    def __setitem__(self, key, val):
        if key not in range(self.SIZE):
            raise IndexError('index out of range: {}'.format(key))
        elif len(val) != self.SIZE:
            raise ValueError('replacement row must be 1×{}'.format(self.SIZE))
        self.rows = tuple(tuple(val) if key == n else self.rows[n]
                          for n in range(self.SIZE))
        assert (len(self.rows) == self.SIZE and
                all(len(row) == self.SIZE for row in self.rows))

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return self.SIZE

    def __mul__(self, mat):
        '''Right-multiply this matrix by another.

        After this operation, the resultant matrix will be the current
        OpenVG matrix.

        Keyword arguments:
            mat -- The other matrix in the multiplication operation.

        '''
        self.make_current()
        vgMultMatrix(mat._as_parameter_)
        result = Matrix()
        result._from_current()
        return result

    def __imul__(self, mat):
        '''Right-multiply this matrix by another, in place.

        After this operation, this matrix will be the current OpenVG
        matrix.

        Keyword arguments:
            mat -- The other matrix in the multiplication operation.

        '''
        self.make_current()
        vgMultMatrix(mat._as_parameter_)
        self._from_current()

    @property
    def is_affine(self):
        '''Determine whether this matrix is affine or projective.'''
        return self[self.SIZE - 1] == (0,) * (self.SIZE - 1) + (1,)

    @property
    def _as_parameter_(self):
        '''Get this matrix formatted for use by foreign functions.

        Note that, although this property is named according to the
        ctypes convention, it cannot be used as-is by ctypes (it is not
        an integer, string or bytes). Fetch this property yourself
        before passing it to a foreign function.

        '''
        return matrix_type(*flatten(self.rows, self.SIZE))

    def _from_current(self):
        '''Update this matrix to match the current OpenVG matrix.'''
        m = matrix_type()
        vgGetMatrix(m)
        self.rows = unflatten(m, self.SIZE)
        assert len(self.rows) == self.SIZE

    def make_current(self):
        '''Make this matrix the current OpenVG matrix.'''
        vgLoadMatrix(self._as_parameter_)

    def rotate(self, rad=None, deg=None):
        '''Apply a rotation to this matrix.

        After this operation, this matrix will be the current OpenVG
        matrix.

        Keyword arguments:
            rad, deg -- The angle of rotation, in radians or degrees,
                respectively. Exactly one of these arguments must be
                supplied. If a positional argument is supplied, it will
                be interpreted as radians.
            
        '''
        # Unlike Python, OpenVG operates in degrees. If we're not given
        # radians...
        if rad is None:
            # ...use the given degrees.
            if deg is None:
                raise TypeError('rotate expected 1 argument, got 0')
        else:
            # But if we are given radians...
            if deg is not None:
                raise TypeError('rotate expected 1 argument, got 2')
            else:
                # ...convert them to degrees.
                deg = degrees(rad)

        self.make_current()
        vgRotate(deg)
        self._from_current()

    def rotate_about(self, cx=0.0, cy=0.0, rad=None, deg=None):
        '''Apply a rotation to this matrix about a given point.

        After this operation, this matrix will be the current OpenVG
        matrix.

        Keyword arguments:
            cx, cy -- The x and y coordinates of the centre of rotation.
                Either or both may be omitted and will default to 0.0.
            rad, deg -- The angle of rotation, in radians or degrees,
                respectively. Exactly one of these arguments must be
                supplied. If a positional argument is supplied, it will
                be interpreted as radians.
            
        '''
        # Unlike Python, OpenVG operates in degrees. If we're not given
        # radians...
        if rad is None:
            # ...use the given degrees.
            if deg is None:
                raise TypeError('rotate_about requires exactly 1 angle '
                                'argument, got 0')
        else:
            # But if we are given radians...
            if deg is not None:
                raise TypeError('rotate_about requires exactly 1 angle '
                                'argument, got 2')
            else:
                # ...convert them to degrees.
                deg = degrees(rad)

        self.make_current()
        vgTranslate(cx, cy)
        vgRotate(deg)
        vgTranslate(-cx, -cy)
        self._from_current()

    def scale(self, sx=1.0, sy=1.0):
        '''Apply a scaling operation to this matrix.

        After this operation, this matrix will be the current OpenVG
        matrix.

        Keyword arguments:
            sx, sy -- The scale factor to apply in the x and y
                directions, respectively. Either or both may be omitted
                and will default to 1.0.
        '''
        self.make_current()
        vgScale(sx, sy)
        self._from_current()

    def shear(self, shx=1.0, shy=1.0):
        '''Apply a shear operation to this matrix.

        After this operation, this matrix will be the current OpenVG
        matrix.

        Keyword arguments:
            shx, shy -- The shear factor to apply in the x and y
                directions, respectively. Either or both may be omitted
                and will default to 1.0.
        '''
        self.make_current()
        vgShear(shx, shy)
        self._from_current()

    def translate(self, tx=0.0, ty=0.0):
        '''Apply a translation to this matrix.

        After this operation, this matrix will be the current OpenVG
        matrix.

        Keyword arguments:
            tx, ty -- The number of units to translate in the x and y
                directions, respectively. Either or both may be omitted
                and will default to 0.0.
        '''
        self.make_current()
        vgTranslate(tx, ty)
        self._from_current()
