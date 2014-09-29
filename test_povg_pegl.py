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

from povg.clip import clear
from povg.context.egl import EGLContext, WindowSurface
from povg.paint import Paint, RGBAColor
from povg.path import Path

from Xlib import X, display as Xdisplay

ctx = EGLContext()
ctx.clear_color = ((0.0, 0.0, 0.0, 1.0))

black = Paint()
black.color = RGBAColor(0, 0, 0, 255)
white = Paint()
white.color = RGBAColor(255, 255, 255, 255)

class TestApp:
    '''A bare-bones X11 window.'''
    def __init__(self, dpy):
        global ctx

        self.Xdisplay = dpy
        self.screen = self.Xdisplay.screen()

        self.window = self.screen.root.create_window(5, 5, 640, 480, 1,
                                                     self.screen.root_depth)
        self.DELETE_WINDOW = self.Xdisplay.intern_atom('WM_DELETE_WINDOW')
        self.PROTOCOLS = self.Xdisplay.intern_atom('WM_PROTOCOLS')

        self.window.set_wm_name('Pegl test: X11')
        self.window.set_wm_protocols((self.DELETE_WINDOW,))

        self.surface = WindowSurface(ctx.display, ctx.config, {},
                                     self.window.id)
        self.path = Path()
        with self.path.queue_segments():
            self.path.vline_to(100, False)
            self.path.hline_to(100, False)
            self.path.vline_to(-100, False)
            self.path.close_path()

        self.window.map()

    def loop(self):
        global black, white

        while True:
            clear((0, 0), 640, 480)
            black.set_stroke()
            white.set_fill()
            self.path.draw()

            ev = self.Xdisplay.next_event()

            if ev.type == X.DestroyNotify:
                raise SystemExit()
            elif ev.type == X.ClientMessage:
                fmt, data = ev.data
                if fmt == 32 and data[0] == self.DELETE_WINDOW:
                    raise SystemExit()


if __name__ == '__main__':
    app = TestApp(Xdisplay.Display())
    app.loop()
