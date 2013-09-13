#!/usr/bin/env python3

# 0. Use EGL to establish a context.
import ctypes
egl = ctypes.CDLL('libEGL.so')
EGL_OPENVG_API = 0x30A1
egl.eglBindAPI(EGL_OPENVG_API)
egl.eglInitialize(egl.eglGetCurrentDisplay(),
                  ctypes.byref(ctypes.c_int(1)),
                  ctypes.byref(ctypes.c_int(4)))

# 1. Can we import Povg?
import povg
from povg.context import Context, FillRule

# 2. Can we establish a context?
ctx = Context()

# 3. Can we get some context values?
print('Maximum kernel size is {}.'.format(ctx.max_kernel_size))
print('Initial fill rule is {}.'.format(ctx.fill_rule))

# 4. Can we set some context values?
ctx.fill_rule = FillRule.NON_ZERO
print('Fill rule is now {}.'.format(ctx.fill_rule))
