#!/usr/bin/env python
# coding: utf8
#
# Copyright 2020 B.Jacob
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from __future__ import print_function
#
# reads a direction from touchpad/pointer and invokes pywin.py to tile the window
#
# requires: XLib, filelock

import os

# minimum distance the pointer must have been moved until a direction is discovered
min_distance = 100
# the cmd to execute
base = os.path.dirname(os.path.realpath(__file__))
cmd = "python " + base + "/pywin.py -s --with-cursor -p "
# wait timeout. Stops program after timeout without input or final decision (e.g. distance was to short)
blocktime = 0.5


import _thread
import sys
from builtins import int, KeyboardInterrupt

import argparse
import math
from Xlib.display import Display
from Xlib.ext import xinput
from argparse import RawTextHelpFormatter
from filelock import FileLock
from threading import Timer

# ===========
x1 = None
y1 = None
blocked = False
is_run_active = True
timer = None


def read_args():
    parser = argparse.ArgumentParser(description='Window-Placement/Window-tiling using touchpad',
                                     formatter_class=RawTextHelpFormatter)

    parser.add_argument('-d', '--durable', dest='durable', action='store_true',
                        help='scale only horizontal')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='print some debugging output')

    parser.add_argument('-t', '--track-distance', dest='distance', metavar="distance", type=int, default=100,
                        help='minimum distance to move pointer before direction is decided')

    args = parser.parse_args()
    return args


def log(arg, *vargs):
    if args.verbose:
        print(arg, *vargs)


def reset():
    global blocked, x, y, is_run_active
    blocked = False
    x = None
    y = None
    if not args.durable:
        log("exit program due to timeout")
        is_run_active = False
        _thread.interrupt_main()  # interrupt main thread
    ##print("reset")


def mouse_to(xp, yp):
    d = Display()
    s = d.screen()
    root = s.root
    root.warp_pointer(xp, yp)
    d.sync()


def run(direction):
    os.system(cmd + direction)


def start_reset_timer():
    global timer
    if timer is not None:
        timer.cancel()
    timer = Timer(blocktime, reset)
    timer.start()


def handle(x, y):
    global x1, y1, blocked, timer
    if blocked or not is_run_active:
        log("program was ended", is_run_active)
        return

    if x1 is None:
        x1 = x
        y1 = y
        start_reset_timer()
        return
    diff_x = x - x1
    diff_y = y1 - y
    distance = math.sqrt(math.fabs(diff_x * diff_x - diff_y * diff_y))

    if distance > min_distance:
        if diff_x == 0:
            diff_x = 0.0001  # avoid division my zero

        slope = diff_y / diff_x
        location = None

        stg = 3  # 3 extreme, 2 , 1 low
        if math.fabs(slope) > 3:
            stg = 3
        if 2.5 >= math.fabs(slope) > 0.4:
            stg = 2
        if math.fabs(slope) < 0.4:
            stg = 1

        if diff_x > 0 and diff_y > 0:  # Q1
            if stg == 1:
                location = "e"
            elif stg == 2:
                location = "ne"
            elif stg == 3:
                location = "n"
        elif diff_x > 0 and diff_y < 0:  # Q2
            if stg == 1:
                location = "e"
            elif stg == 2:
                location = "se"
            elif stg == 3:
                location = "s"
        elif diff_x < 0 and diff_y < 0:  # Q3
            if stg == 1:
                location = "w"
            elif stg == 2:
                location = "sw"
            elif stg == 3:
                location = "s"
        elif diff_x < 0 and diff_y > 0:
            if stg == 1:
                location = "w"
            elif stg == 2:
                location = "nw"
            elif stg == 3:
                location = "n"

        log(location, diff_y, diff_y, "slope", slope, "stg", stg, "direction", location)

        blocked = True
        mouse_to(int(x1), int(y1))

        timer.cancel()

        if args.durable:
            start_reset_timer()

        else:
            run(location)
            if timer is not None:
                timer.cancel()
            sys.exit(0)

args = read_args()

def main(argv):
    global timer, is_run_active, args, min_distance
    with FileLock("mousy.lock", timeout=0.3):
        log("Lock acquired.")  # avoid multiple runs  the same time

        min_distance = args.distance

        start_reset_timer()

        display = Display()
        try:
            extension_info = display.query_extension('XInputExtension')

            version_info = display.xinput_query_version()
            log('Found XInput version %u.%u' % (
                version_info.major_version,
                version_info.minor_version,
            ))

            screen = display.screen()
            screen.root.xinput_select_events([(xinput.AllDevices, xinput.MotionMask)])

            while is_run_active:
                try:
                    event = display.next_event()
                    x = event.data.root_x
                    y = event.data.root_y
                    handle(x, y)
                except KeyboardInterrupt as e:
                    log("interrupted")
        finally:
            display.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
