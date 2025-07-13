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
from Xlib import X, display  # python-xlib

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

gi.require_version("Wnck", "3.0")
from gi.repository import Wnck

import json
import os
import sys
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
    x = round(rect[0] + rect[2] / 2)
    y = round(rect[1] + rect[3] / 2)
    if verbose:
        print("new win pos:" + str(rect))
        print ("new x,y" + str(x) + "," + str(y))
    root.warp_pointer(x, y)
    d.sync()


def discoverScreens():
    """
    Discover screens and their work areas, accounting for taskbars/panels on any side
    """
    screens = []
    display = Gdk.Display.get_default()
    
    if display is None:
        if verbose:
            print("Could not get default display, falling back to hardcoded screen config")
        return [{"name": "screen-1", "x": 0, "y": 0, "width": 1920, "height": 1080}]
    
    n_monitors = display.get_n_monitors()
    if verbose:
        print(f"Found {n_monitors} monitors")
    
    for monitor_idx in range(0, n_monitors):
        monitor = display.get_monitor(monitor_idx)
        if monitor is None:
            continue
            
        # Get physical monitor geometry
        monitor_geometry = monitor.get_geometry()
        
        # Try to get work area (area not occupied by panels/taskbars)
        work_area = None
        use_fallback = False
        
        try:
            # This method is available in newer GTK versions
            work_area = monitor.get_workarea()
            if verbose:
                print(f"  get_workarea() returned: {work_area.x}x{work_area.y} {work_area.width}x{work_area.height}")
            
            # Check if work area equals monitor area (indicates no panels detected)
            if (work_area.x == monitor_geometry.x and work_area.y == monitor_geometry.y and
                work_area.width == monitor_geometry.width and work_area.height == monitor_geometry.height):
                if verbose:
                    print("  get_workarea() found no panels, forcing fallback detection")
                use_fallback = True
                
        except AttributeError:
            if verbose:
                print("  get_workarea() not available, using fallback panel detection")
            use_fallback = True
        except Exception as e:
            if verbose:
                print(f"  get_workarea() failed: {e}, using fallback panel detection")
            use_fallback = True
        
        # Force fallback if GTK didn't detect panels or if work area detection failed
        if work_area is None or use_fallback:
            if verbose:
                print("  Using fallback panel detection...")
            work_area = detectPanelsAndCalculateWorkArea(monitor_geometry)
        
        name = "screen-" + str(monitor_idx + 1)
        
        # Use work area for tiling calculations
        screen_info = {
            "name": name,
            "x": work_area.x,
            "y": work_area.y, 
            "width": work_area.width,
            "height": work_area.height,
            # Store original geometry for reference
            "monitor_x": monitor_geometry.x,
            "monitor_y": monitor_geometry.y,
            "monitor_width": monitor_geometry.width,
            "monitor_height": monitor_geometry.height
        }
        
        if verbose:
            print(f"Monitor {monitor_idx + 1}:")
            print(f"  Physical: {monitor_geometry.x}x{monitor_geometry.y} {monitor_geometry.width}x{monitor_geometry.height}")
            print(f"  Work area: {work_area.x}x{work_area.y} {work_area.width}x{work_area.height}")
            
            # Calculate panel positions for debugging
            if work_area.x > monitor_geometry.x:
                print(f"  Left panel: {work_area.x - monitor_geometry.x}px")
            if work_area.y > monitor_geometry.y:
                print(f"  Top panel: {work_area.y - monitor_geometry.y}px")
            if (monitor_geometry.x + monitor_geometry.width) > (work_area.x + work_area.width):
                print(f"  Right panel: {(monitor_geometry.x + monitor_geometry.width) - (work_area.x + work_area.width)}px")
            if (monitor_geometry.y + monitor_geometry.height) > (work_area.y + work_area.height):
                print(f"  Bottom panel: {(monitor_geometry.y + monitor_geometry.height) - (work_area.y + work_area.height)}px")
        
        screens.append(screen_info)
    
    return screens


def detectPanelsAndCalculateWorkArea(monitor_geometry):
    """
    Fallback method to detect XFCE panels and calculate work area manually
    """
    if verbose:
        print(f"  Fallback detection for monitor: {monitor_geometry.x}x{monitor_geometry.y} {monitor_geometry.width}x{monitor_geometry.height}")
    
    # Start with full monitor as work area
    work_x = monitor_geometry.x
    work_y = monitor_geometry.y
    work_width = monitor_geometry.width
    work_height = monitor_geometry.height
    
    panels_found = 0
    
    try:
        # Get the window manager screen to enumerate windows
        wnck_screen = Wnck.Screen.get_default()
        if wnck_screen is None:
            if verbose:
                print("  Warning: Could not get Wnck screen for panel detection")
        else:
            wnck_screen.force_update()
            
            # Look for XFCE panel windows
            for window in wnck_screen.get_windows():
                if window.get_window_type() == Wnck.WindowType.DOCK:
                    # This is likely a panel/dock
                    geom = window.get_geometry()
                    win_x, win_y, win_w, win_h = geom
                    
                    if verbose:
                        print(f"    Found dock window: '{window.get_name()}' at {win_x}x{win_y} {win_w}x{win_h}")
                    
                    # Check if this panel intersects with our monitor
                    if (win_x < monitor_geometry.x + monitor_geometry.width and
                        win_x + win_w > monitor_geometry.x and
                        win_y < monitor_geometry.y + monitor_geometry.height and
                        win_y + win_h > monitor_geometry.y):
                        
                        panels_found += 1
                        if verbose:
                            print(f"      Panel intersects with monitor")
                        
                        # Determine panel position and adjust work area
                        # Top panel (within 10px of top edge, spans most of width)
                        if (win_y <= monitor_geometry.y + 10 and 
                            win_w > monitor_geometry.width * 0.5):  # Reduced threshold
                            panel_bottom = win_y + win_h
                            if panel_bottom > work_y:
                                adjust = panel_bottom - work_y
                                work_y += adjust
                                work_height -= adjust
                                if verbose:
                                    print(f"      Detected TOP panel: adjusted work_y to {work_y}, work_height to {work_height}")
                        
                        # Bottom panel (within 10px of bottom edge, spans most of width)
                        elif (win_y + win_h >= monitor_geometry.y + monitor_geometry.height - 10 and
                              win_w > monitor_geometry.width * 0.5):  # Reduced threshold
                            panel_top = win_y
                            if panel_top < work_y + work_height:
                                old_height = work_height
                                work_height = panel_top - work_y
                                if verbose:
                                    print(f"      Detected BOTTOM panel: reduced work_height from {old_height} to {work_height}")
                        
                        # Left panel (within 10px of left edge, spans most of height)
                        elif (win_x <= monitor_geometry.x + 10 and
                              win_h > monitor_geometry.height * 0.5):  # Reduced threshold
                            panel_right = win_x + win_w
                            if panel_right > work_x:
                                adjust = panel_right - work_x
                                work_x += adjust
                                work_width -= adjust
                                if verbose:
                                    print(f"      Detected LEFT panel: adjusted work_x to {work_x}, work_width to {work_width}")
                        
                        # Right panel (within 10px of right edge, spans most of height)
                        elif (win_x + win_w >= monitor_geometry.x + monitor_geometry.width - 10 and
                              win_h > monitor_geometry.height * 0.5):  # Reduced threshold
                            panel_left = win_x
                            if panel_left < work_x + work_width:
                                old_width = work_width
                                work_width = panel_left - work_x
                                if verbose:
                                    print(f"      Detected RIGHT panel: reduced work_width from {old_width} to {work_width}")
                        else:
                            if verbose:
                                print(f"      Panel position not recognized as standard edge panel")
                    else:
                        if verbose:
                            print(f"      Panel does not intersect with monitor")
            
            if verbose:
                print(f"  Found {panels_found} panel(s) on this monitor")
    
    except Exception as e:
        if verbose:
            print(f"  Error detecting panels: {e}")
    
    if verbose:
        if panels_found > 0:
            print(f"  Final work area: {work_x}x{work_y} {work_width}x{work_height}")
        else:
            print(f"  No panels found - using full monitor: {work_x}x{work_y} {work_width}x{work_height}")
    
    # Create a simple object to mimic Gdk.Rectangle
    class WorkArea:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
    
    return WorkArea(work_x, work_y, work_width, work_height)


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
        # Use monitor coordinates for intersection detection (not work area)
        monitor_x = screen.get('monitor_x', screen['x'])
        monitor_y = screen.get('monitor_y', screen['y']) 
        monitor_width = screen.get('monitor_width', screen['width'])
        monitor_height = screen.get('monitor_height', screen['height'])
        
        # screens without intersections must not be relevant here
        if not boxIntersects(x, y, x + width, y + height, 
                           monitor_x, monitor_y, 
                           monitor_x + monitor_width, monitor_y + monitor_height):
            if verbose:
                print(" No intersection with: " + str(screen["name"]))
            continue

        x1 = max(x, monitor_x)
        y1 = max(y, monitor_y)
        x2 = min(x + width, monitor_x + monitor_width)
        y2 = min(y + height, monitor_y + monitor_height)

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
        print(f" Screen work area: {bestMatch['x']}x{bestMatch['y']} {bestMatch['width']}x{bestMatch['height']}")

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


def calcNewPos(screen, position, factor, geometryRaw, currentPos, verticallyOnly=False, horizontalOnly=False):
    gravity = Wnck.WindowGravity.NORTHWEST
    
    # Work area coordinates (should already exclude panels)
    work_x = screen["x"]
    work_y = screen["y"] 
    work_width = screen["width"]
    work_height = screen["height"]
    
    if verbose:
        print(f"calcNewPos: Using work area {work_x}x{work_y} {work_width}x{work_height} for position '{position}' with factor {factor}")
    
    # For factor=1 (100%), always use full dimensions to avoid any rounding issues
    if factor == 1.0:
        calc_width = work_width
        calc_height = work_height
    else:
        calc_width = round(work_width / factor)
        calc_height = round(work_height / factor)
    
    if position == 'n':
        y = work_y
        x = work_x
        width = work_width
        height = calc_height

    elif position == 'ne':
        width = calc_width
        height = calc_height
        y = work_y
        # Ensure right edge aligns perfectly
        x = work_x + work_width - width
        
        if horizontalOnly:
            width = calc_width
            height = currentPos[3]
        if verticallyOnly:
            width = currentPos[2]
            height = calc_height
            x = currentPos[0]

    elif position == 'e':
        width = calc_width
        y = work_y
        # Ensure right edge aligns perfectly
        x = work_x + work_width - width
        height = work_height

    elif position == 'se':
        width = calc_width
        height = calc_height
        y = work_y + work_height - height  # Bottom alignment
        x = work_x + work_width - width    # Right alignment
        
        if horizontalOnly:
            width = calc_width
            height = currentPos[3]
            x = work_x + work_width - width  # Maintain right alignment
            y = work_y + work_height - currentPos[3]  # Maintain bottom alignment
        if verticallyOnly:
            x = currentPos[0]
            width = currentPos[2]
            height = calc_height
            # y already calculated correctly above

    elif position == 's':
        height = calc_height
        # Ensure bottom edge aligns perfectly
        y = work_y + work_height - height
        x = work_x
        width = work_width

    elif position == 'sw':
        width = calc_width
        height = calc_height
        x = work_x
        y = work_y + work_height - height  # Always align to bottom
        
        if horizontalOnly:
            width = calc_width
            height = currentPos[3]
            y = work_y + work_height - currentPos[3]  # Maintain bottom alignment
        if verticallyOnly:
            width = currentPos[2]
            height = calc_height
            # y already calculated correctly above

    elif position == 'w':
        width = calc_width
        y = work_y
        x = work_x
        height = work_height

    elif position == 'nw':
        width = calc_width
        height = calc_height
        y = work_y
        x = work_x
        
        if horizontalOnly:
            width = calc_width
            height = currentPos[3]
        if verticallyOnly:
            width = currentPos[2]
            height = calc_height

    elif position == 'center':
        width = calc_width
        height = work_height
        y = work_y
        # Center horizontally with integer division for perfect centering
        x = work_x + (work_width - width) // 2

    if verbose:
        right_edge = x + width if 'width' in locals() else 'N/A'
        bottom_edge = y + height if 'height' in locals() else 'N/A'
        print(f"  Calculated: x={x}, y={y}, w={width}, h={height}")
        print(f"  Right edge: {right_edge}, Bottom edge: {bottom_edge}")
        print(f"  Work area right: {work_x + work_width}, Work area bottom: {work_y + work_height}")

    return (x, y, width, height, gravity)


def get_window_id(window):
    # read the id of the window
    xid = window.get_xid()
    return xid


wnck_screen = Wnck.Screen.get_default()
if wnck_screen is None:
    print("Error: No X11 display found. This script requires XFCE/X11 environment.")
    print("Make sure you're running this on a system with XFCE desktop environment.")
    sys.exit(1)
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

if autoDiscoverScreens:
    # read screens and their work areas from gtk - automatically handles panels/taskbars
    screens = discoverScreens()

# get current window
wnck_screen.force_update()  # recommended by documenation
active = wnck_screen.get_active_window()

# Detect application type for specific handling
app_name = active.get_application().get_name().lower() if active.get_application() else ""
window_class = active.get_class_group_name().lower() if active.get_class_group_name() else ""
is_terminal = any(term in app_name or term in window_class for term in ['terminal', 'xterm', 'konsole', 'gnome-terminal'])

if verbose:
    print(f"Active window: {active.get_name()}")
    print(f"Application: {app_name}")
    print(f"Class: {window_class}")
    print(f"Is terminal: {is_terminal}")

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
        print("factor" + str(factor))
        print(position)
        print(screen)
    newPos = calcNewPos(screen, position, newFactor, geometryRaw, currentPos, args.vert, args.hori)


else:
    newPos = calcNewPos(screen, position, factor, geometryRaw, currentPos, args.vert, args.hori)

if verbose:
    print("New Geometry calculated " + str(newPos))
# find difference of window decoration and take it into the calculation


# find difference of window decoration and use it for calculation
correctureY = geometryRaw[1] - currentPos[1]
correctureX = geometryRaw[0] - currentPos[0]

# Apply terminal-specific corrections if needed
if is_terminal:
    # Terminal applications often have additional spacing issues
    # Common fixes: reduce bottom spacing, account for character grid alignment
    terminal_correction_x = 0
    terminal_correction_y = 0
    
    # For bottom-aligned positions (s, sw, se), terminals often need adjustment
    if position in ['s', 'sw', 'se']:
        terminal_correction_y = -2  # Reduce gap by 2px (adjust as needed)
    
    # For right-aligned positions (e, ne, se), terminals might need adjustment  
    if position in ['e', 'ne', 'se']:
        terminal_correction_x = -1  # Reduce gap by 1px (adjust as needed)
    
    if verbose:
        print(f"Terminal corrections: x={terminal_correction_x}, y={terminal_correction_y}")
    
    correctureX += terminal_correction_x
    correctureY += terminal_correction_y

if verbose:
    print(f"Final corrections: x={correctureX}, y={correctureY}")

active.set_geometry(gravity=newPos[4],
                    geometry_mask=flags,
                    x=round(newPos[0] - correctureX),
                    y=round(newPos[1] - correctureY),
                    width=round(newPos[2]),
                    height=round(newPos[3]))

if args.mouse:
    # keep the active window in foreground otherwise mouse might focus an other window
    Wnck.Window.make_above(active)  # - always on top on
    Wnck.Window.unmake_above(active)  # - always on top off
    placeMouseOver((round(newPos[0] - correctureX), round(newPos[1] - correctureY), round(newPos[2]), round(newPos[3])))
