#!/usr/bin/env python3

'''VGU utility library package.'''

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

__all__ = ['native', 'vgu_error_codes']

# Local imports.
from .. import (BadHandleError, IllegalArgumentError, OutOfMemoryError,
                PathCapabilityError, BadWarpError)

vgu_error_codes = {0: None, # No error.
                   0xF000: BadHandleError, 0xF001: IllegalArgumentError,
                   0xF002: OutOfMemoryError, 0xF003: PathCapabilityError,
                   0xF004: BadWarpError}
