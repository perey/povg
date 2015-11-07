#!/usr/bin/env python3

'''Test Povg using Pegl for context management.

The window is created using X11, with code borrowed from the X11 test
case in Pegl.

'''
# Copyright © 2014 Tim Pederick.
# Based on examples/draw.py from python-x11:
#     Copyright © 2000 Peter Liljenberg <petli@ctrl-c.liu.se>
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

import time

from povg.clip import clear
from povg.context.egl import EGLContext, WindowSurface
from povg.paint import Paint, RGBAColor
from povg.path import Path

from Xlib import X, display as Xdisplay

FRAMERATE = 30
WIDTH = 640
HEIGHT = 480

ctx = EGLContext()
ctx.display.initialize()

class TestApp:
    '''A bare-bones X11 window.'''
    def __init__(self, dpy):
        global ctx

        self.Xdisplay = dpy
        self.screen = self.Xdisplay.screen()

        self.window = self.screen.root.create_window(5, 5, WIDTH, HEIGHT, 1,
                                                     self.screen.root_depth)
        self.DELETE_WINDOW = self.Xdisplay.intern_atom('WM_DELETE_WINDOW')
        self.PROTOCOLS = self.Xdisplay.intern_atom('WM_PROTOCOLS')

        self.window.set_wm_name('Pegl/Povg test: X11')
        self.window.set_wm_protocols((self.DELETE_WINDOW,))

        self.surface = WindowSurface(ctx.display, ctx.config, {},
                                     self.window.id)
        ctx.make_current(draw_surface=self.surface)
        ctx.clear_color = ((1.0, 1.0, 1.0, 1.0))
        ctx.stroke_line_width = 3.0

        self.fill = Paint(color=RGBAColor(0, 255, 0, 127))
        self.fill.set_fill()
        self.stroke = Paint(color=RGBAColor(0, 0, 0, 255))
        self.stroke.set_stroke()

        self.path = Path()
        with self.path.queue_segments():
            self.path.move_to((100, 100))
            self.path.arc_to((50, 50), 0, (0, 100), is_clockwise=True,
                             is_absolute=False)
            self.path.hline_to(100, False)
            self.path.line_to((-50, -75), False)
            self.path.close_path()

        self.window.map()

    def loop(self):
        global ctx, red, cyan

        while True:
            ctx.make_current(draw_surface=self.surface)
            clear((0, 0), WIDTH, HEIGHT)
            self.path.draw()
            self.surface.swap_buffers()

            if self.Xdisplay.pending_events() > 0:
                ev = self.Xdisplay.next_event()

                if ev.type == X.DestroyNotify:
                    raise SystemExit()
                elif ev.type == X.ClientMessage:
                    fmt, data = ev.data
                    if fmt == 32 and data[0] == self.DELETE_WINDOW:
                        raise SystemExit()

            self.sleep()

    def sleep(self):
        time.sleep(1 / FRAMERATE)


if __name__ == '__main__':
    app = TestApp(Xdisplay.Display())
    app.loop()
