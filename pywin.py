#!/usr/bin/env python
# coding: utf8
#
# Copyright 2018 B.Jacob
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import argparse
import gi
from Xlib import X, display # python-xlib
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
gi.require_version("Wnck", "3.0")
from gi.repository import Wnck

import json
import os
from argparse import RawTextHelpFormatter

screens = [
    {"name": "screen1", "x": 0, "y": 0, "width": 2560, "height": 1440 - 32},
    {"name": "screen2", "x": 2560, "y": 0, "width": 2560, "height": 1440},
    {"name": "screen3", "x": 2560 + 2560, "y": 0, "width": 1280, "height": 1024}
]
# switch off to use screens defined above
autoDiscoverScreens = True

storageFile = "/tmp/pywin.json"

choices = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']

def placeMouseOver(rect):
    d = display.Display()
    s = d.screen()
    root = s.root
    x = int(rect[0] + rect[2]/2)
    y = int(rect[1] + rect[3]/2)
    print("new win pos:"+str(rect))
    print ("new x,y"+ str(x)+","+str(y))
    root.warp_pointer(x,y)
    d.sync()


def discoverScreens():
    # TODO discover taskbars on any side of the screen
    # (e.g. make a window fullscreen and take coords?)
    screens = []
    display = Gdk.Display.get_default()
    for x in range(0, display.get_n_monitors()):
        screenDim = display.get_monitor(x).get_geometry()
        if screenDim is None:
            continue
        name = "screen-" + str(x + 1)
        screens.append({"name": name, "x": screenDim.x, "y": screenDim.y,
                        "width": screenDim.width, "height": screenDim.height})
    return screens


def boxIntersects(leftA, topA, rightA, bottomA, leftB, topB, rightB, bottomB):
    return not (leftA > rightB or
                rightA < leftB or
                topA > bottomB or
                bottomA < topB)


def findBounds(x, y, width, height):
    if verbose:
        print("Find best matching screen for window:")

    bestMatch = screens[0]  # always use a default
    match = -1000
    for screen in screens:
        # screens without intersections must not be relevant here
        if not boxIntersects(x, y, x + width, y + height, screen['x'], screen['y'], screen['x'] + screen['width'],
                             screen['y'] + screen['height']):
            if verbose:
                print(" No intersection with: " + str(screen["name"]))
            continue

        x1 = max(x, screen['x'])
        y1 = max(y, screen['y'])
        x2 = min(x + width, screen['x'] + screen['width'])
        y2 = min(y + height, screen['y'] + screen['height'])

        sizeWindow = width * height
        sizeOnScreen = (x2 - x1) * (y2 - y1)
        percentOnScreen = sizeOnScreen * 100 / sizeWindow

        if verbose:
            print(" " + str(percentOnScreen) + "% are on: " + str(screen["name"]))

        if match < percentOnScreen:
            # a window belongs to the screen that renders most parts of it
            match = percentOnScreen
            bestMatch = screen

    # always return screen 1
    if verbose:
        print(" Using: " + str(bestMatch["name"]) + " as best match")

    return bestMatch


def read_args():
    parser = argparse.ArgumentParser(description='Window-Placement/Window-tiling', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-p', '--pos', dest='position', metavar="position", required=True, choices=choices,
                        help='Direction to place window. Using abbreviations for directions like n=north ne=northeast and so on. Use one of:' +
                             (','.join(choices)))

    parser.add_argument('-f', '--factor', dest='factor', metavar="factor", type=int, default=2,
                        help='default scale factor ')

    parser.add_argument('-s', '--stateful', dest='stateful', action='store_true',
                        help='remember window sizing by storing some data under: ' + storageFile)

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='print some debugging output')
    parser.add_argument('-o', '--horizontal', dest='hori', action='store_true',
                        help='scale only horizontal')
    parser.add_argument('-e', '--vertically', dest='vert', action='store_true',
                        help='scale only vertical')
    parser.add_argument('-c', '--with-cursor', dest='mouse', action='store_true', default=False,
                        help='place mouse cursor over moved window. Subsequent invocations should address same window'
                             ' if system activates windows on hover')
    parser.add_argument('-m', '--my-factors', dest='myfactor', metavar="scale-factors", default="1,1.334,1.5,2,3,4",
                        help='Comma delimited list of scale-factors to use. e.g. \"1,1.5,2,3\" This requires stateful option.')

    args = parser.parse_args()
    return args


def calcNewPos(screen, position, factor, geometryRaw,currentPos, verticallyOnly=False, horizontalOnly=False ):
    gravity = Wnck.WindowGravity.NORTHWEST
    if position == 'n':
        y = screen["y"]
        x = screen["x"]
        width = screen["width"]
        height = screen["height"] / factor

    if position == 'ne':
        y = screen["y"]
        x = screen["x"] + screen["width"] - screen["width"] / factor
        if not horizontalOnly and not verticallyOnly:
            width = screen["width"] / factor
            height = screen["height"] / factor
        if horizontalOnly:
            width = screen["width"] / factor
            height =currentPos.heightp
        if verticallyOnly:
            width =  currentPos.widthp
            height = screen["height"] / factor
            x = currentPos.xp

    if position == 'e':
        y = screen["y"]
        x = screen["x"] + screen["width"] - screen["width"] / factor
        width = screen["width"] / factor
        height = screen["height"]

    if position == 'se':
        y = screen["y"] + screen["height"] - screen["height"] / factor
        x = screen["x"] + screen["width"] - screen["width"] / factor
        if not horizontalOnly and not verticallyOnly:
            width = screen["width"] / factor
            height = screen["height"] / factor
        if horizontalOnly:
            width = screen["width"] / factor
            height =currentPos.heightp
            y = currentPos.yp
        if verticallyOnly:
            x = currentPos.xp
            width =  currentPos.widthp
            height = screen["height"] / factor

    if position == 's':
        y = screen["y"] + screen["height"] - screen["height"] / factor
        x = screen["x"]
        width = screen["width"]
        height = screen["height"] / factor

    if position == 'sw':
        y = screen["y"] + screen["height"] - screen["height"] / factor
        x = screen["x"]
        if not horizontalOnly and not verticallyOnly:
            width = screen["width"] / factor
            height = screen["height"] / factor
        if horizontalOnly:
            width = screen["width"] / factor
            height =currentPos.heightp
            y = currentPos.yp
        if verticallyOnly:
            width =  currentPos.widthp
            height = screen["height"] / factor

    if position == 'w':
        y = screen["y"]
        x = screen["x"]
        width = screen["width"] / factor
        height = screen["height"]

    if position == 'nw':
        y = screen["y"]
        x = screen["x"]
        if not horizontalOnly and not verticallyOnly:
            width = screen["width"] / factor
            height = screen["height"] / factor
        if horizontalOnly:
            width = screen["width"] / factor
            height =currentPos.heightp
        if verticallyOnly:
            width =  currentPos.widthp
            height = screen["height"] / factor


    if position == 'center':
        # active.maximize()
        # sys.exit(0)
        width = screen["width"] / factor
        height = screen["height"]
        y = screen["y"]
        x = ((screen["x"] + (screen["width"] / 2)) - width / 2)

    return (x, y, width, height, gravity)


def get_window_id(window):
    # read the id of the window
    xid = window.get_xid()
    return xid


if autoDiscoverScreens:
    # read screens and their config from gtk
    screens = discoverScreens()
    # taskbar on screen 1
    screens[0]["height"] = screens[0]["height"] - 32

screen = Wnck.Screen.get_default()
# while gtk.events_pending(): #do something magic
#    gtk.main_iteration()

# read parameters
args = read_args()
verbose = args.verbose
factor = args.factor
position = args.position
stateful = args.stateful
factors = []
for elem in args.myfactor.split(","):
    factors.append(float(elem))

# get current window
screen.force_update()  # recommended by documenation
active = screen.get_active_window()

# read dimensions of window
currentPos = (winX, winY, winW, winH) = active.get_geometry()

# find out the screen the active window lives on
screen = findBounds(max(0, winX), max(0, winY), winW, winH)

flags = Wnck.WindowMoveResizeMask.X | \
        Wnck.WindowMoveResizeMask.Y | \
        Wnck.WindowMoveResizeMask.WIDTH | \
        Wnck.WindowMoveResizeMask.HEIGHT
active.unmaximize()

#
# Note: set_geometry position seems to works relative to current window
#
geometryRaw = active.get_client_window_geometry()
if verbose:
    print("Geometry raw:" + str(geometryRaw))
    print("current Pos: " + str(currentPos))

if (stateful):
    if verbose:
        print("Decide next scale factor" + storageFile)

    data = {}
    if os.path.isfile(storageFile):
        with open(storageFile) as json_data:
            data = json.load(json_data)

    id = get_window_id(active)
    if str(id) in data:
        currentFactor = float(data[str(id)])
    else:
        currentFactor = 1

    if currentFactor in factors:
        idx = factors.index(currentFactor)
    else:
        idx = 0

    # now we select the index of the next scale factors
    idx = (idx + 1) % len(factors)
    # and now lookup the next factor
    newFactor = factors[idx]
    if verbose:
        print(" Next scale-factor for window with id:" + str(id) + " is:" + str(newFactor))
    # and remember the factor
    data[str(id)] = str(newFactor)
    # store info
    if verbose:
        print(" Write state to file:" + str(storageFile))

    with open(storageFile, 'w') as outfile:
        json.dump(data, outfile)

    if verbose:
        print("factor"+ str(factor))
        print(position)
        print(screen)
    newPos = calcNewPos(screen, position, newFactor, geometryRaw,currentPos, args.vert, args.hori)


else:
    newPos = calcNewPos(screen, position, factor, geometryRaw,currentPos, args.vert, args.hori)

if verbose:
    print("New Geometry calculated " + str(newPos))
# find difference of window decoration and take it into the calculation


# find difference of window decoration and use it for calculation
correctureY = geometryRaw[1] - currentPos[1]
correctureX = geometryRaw[0] - currentPos[0]

active.set_geometry(gravity=newPos[4],
                    geometry_mask=flags,
                    x=int(newPos[0] - correctureX),
                    y=int(newPos[1] - correctureY),
                    width=int(newPos[2]),
                    height=int(newPos[3]))

if args.mouse:
    # keep the active window in foreground otherwise mouse might focus an other window
    Wnck.Window.make_above(active) #- always on top on
    Wnck.Window.unmake_above(active) #- always on top off
    placeMouseOver((int(newPos[0] - correctureX),int(newPos[1] - correctureY),int(newPos[2]), int(newPos[3])))
