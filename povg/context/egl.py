#!/usr/bin/env python3

'''OpenVG context access and surface creation using EGL.'''

# Copyright © 2013-14 Tim Pederick.
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

# Pegl imports.
import pegl.attribs
import pegl.config
import pegl.context
import pegl.display
import pegl.surface

# Local imports.
from . import Context

# And now the unholy offspring of an EGL context and an OpenVG context!
class EGLContext(pegl.context.Context, Context):
    '''Represents an EGL context configured for OpenVG.

    Instance attributes:
    display, config, ctxhandle, render_buffer -- Inherited from
        pegl.context.Context.
    api -- Inherited from pegl.context.Context. Should always be the
        string 'OpenVG'.
    api_version -- Inherited from pegl.context.Context, but never
        relevant.

    Access to OpenVG-specific context parameters is possible through
    attributes inherited from Context. Note that these parameters apply
    to the current OpenVG context, which is not necessarily the Context
    instance being used to query them. You should ensure that your
    context instance is current (using make_current()) before querying
    or setting any of these parameters.

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

        # Sanity check.
        assert self.api == 'OpenVG'

# TODO: Subclass pegl.surface.WindowSurface and provide new names (without the
# openvg_ prefix) for openvg_alpha_premultiplied and openvg_colorspace? And
# possibly allow these (and render_buffer) to be set in the constructor without
# needing to mess with a pegl.attribs.AttribList?
WindowSurface = pegl.surface.WindowSurface

# TODO: As above, possibly with some shortcuts for binding the Pbuffer to an
# OpenVG Image.
PbufferSurface = pegl.surface.PbufferSurface
