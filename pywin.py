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
import gtk
import json
import os
import wnck
from argparse import RawTextHelpFormatter

storageFile="/tmp/pywin.json"

choices = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']

# correcting miss-calculations this might be related to decorations of the window-manager read from somwhere in system
correctY = -32
correctX = -2
correctW = 0
correctH = 0

# Adjust here and define the screens and their positions. TODO: read them from somewhere from system
screens = [
  {"name": "screen1", "x": 0, "y": 0, "width": 2560, "height": 1440},
  {"name": "screen2", "x": 2560, "y": 0, "width": 2560, "height": 1440},
  {"name": "screen3", "x": 2560 + 2560, "y": 0, "width": 1280, "height": 1024}
]


def boxIntersects(leftA, topA, rightA, bottomA, leftB, topB, rightB, bottomB):

  return not(leftA > rightB or
    rightA < leftB or
    topA > bottomB or
    bottomA < topB)


def findBounds(x, y, width, height):
  if verbose:
    print "Find best matching screen for window:"

  bestMatch = screens[0] # always use a default
  match = -1000
  for screen in screens:
    # screens without intersections must not be relevant here 
    if not boxIntersects(x, y , x+width, y+height, screen['x'], screen['y'], screen['x'] + screen['width'], screen['y'] + screen['height']):
      if verbose:
        print " No intersection with: " + str(screen["name"])
      continue


    x1 = max(x, screen['x'])
    y1 = max(y, screen['y'])
    x2 = min(x + width,  screen['x'] + screen['width'])
    y2 = min(y + height, screen['y'] + screen['height'])

    sizeWindow = width * height 
    sizeOnScreen = (x2-x1) * (y2-y1)
    percentOnScreen = sizeOnScreen*100/sizeWindow

    if verbose: 
        print " " + str(percentOnScreen) + "% are on: " + str(screen["name"])

    if match < percentOnScreen:
      # a window belongs to the screen that renders most parts of it 
      match = percentOnScreen
      bestMatch = screen

  # always return screen 1
  if verbose:
    print " Using: " + str(bestMatch["name"]) + " as best match"

  return bestMatch


def read_args():
  parser = argparse.ArgumentParser(description='Window-Placement/Window-tiling', formatter_class=RawTextHelpFormatter)
  parser.add_argument('-p', '--pos', dest='position', metavar="position", required=True, choices=choices,
                      help='Direction to place window. Using abbreviations for directions like n=north ne=northeast and so on. Use one of:'+
                           (','.join(choices)))

  parser.add_argument('-f', '--factor', dest='factor', metavar="factor", type=int,default=2,
                      help='default scale factor ')

  parser.add_argument('-s', '--stateful', dest='stateful', action='store_true',
                      help='remember window sizing by storing some data under: '+ storageFile)

  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                      help='print some debugging output')

  parser.add_argument('-m', '--my-factors', dest='myfactor', metavar="scale-factors", default="1,1.5,2,3",
                      help='Comma delimited list of scale-factors to use. e.g. \"1,1.5,2,3\" This requires stateful option to work.')

  args = parser.parse_args()
  return args


def calcNewPos(screen,position, factor):

  gravity = wnck.WINDOW_GRAVITY_NORTHWEST
  if position == 'n':
    y = screen["y"]
    x = screen["x"]
    width = screen["width"]
    height = screen["height"] / factor

  if position == 'ne':
    y = screen["y"]
    x = screen["x"] + screen["width"] - screen["width"] / factor
    width = screen["width"] / factor
    height = screen["height"] / factor

  if position == 'e':
    y = screen["y"]
    x = screen["x"] + screen["width"] - screen["width"] / factor
    width = screen["width"] / factor
    height = screen["height"]

  if position == 'se':
    y = screen["y"] + screen["height"] - screen["height"] / factor
    x = screen["x"] + screen["width"] - screen["width"] / factor
    width = screen["width"] / factor
    height = screen["height"] / factor

  if position == 's':
    y = screen["y"] + screen["height"] - screen["height"] / factor
    x = screen["x"]
    width = screen["width"]
    height = screen["height"] / factor

  if position == 'sw':
    y = screen["y"] + screen["height"] - screen["height"] / factor
    x = screen["x"]
    width = screen["width"] / factor
    height = screen["height"] / factor

  if position == 'w':
    y = screen["y"]
    x = screen["x"]
    width = screen["width"] / factor
    height = screen["height"]

  if position == 'nw':
    y = screen["y"]
    x = screen["x"]
    width = screen["width"] / factor
    height = screen["height"] / factor

  if position == 'center':
    #active.maximize()
    #sys.exit(0)
    #gravity = wnck.WINDOW_GRAVITY_CENTER
    width = screen["width"] / factor
    height = screen["height"]
    y = screen["y"]
    x = ((screen["x"] + (screen["width"] /2)) - width/2)
  return (x,y,width,height, gravity)


def get_window_id(window):
  # read the id of the window
  xid = window.get_xid()
  return xid


screen = wnck.screen_get_default()
while gtk.events_pending(): #do something magic
  gtk.main_iteration()

# read parameters
args = read_args()
position = args.position
factor = args.factor
stateful = args.stateful
factors = []
for elem in args.myfactor.split(","):
  factors.append(float(elem))

verbose = args.verbose

# get current window
active = screen.get_active_window()

# read dimensions of window
currentPos = (winX, winY, winW, winH) = active.get_geometry()


# find out the screen the active window lives on
screen = findBounds(max(0, winX), max(0, winY), winW, winH)


if(stateful):
  if verbose:
    print "Decide next scale factor" + storageFile
  
  data =  {}
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
  idx = (idx +1) % len(factors)
  # and now lookup the next factor
  newFactor = factors[idx]
  if verbose:
    print " Next scale-factor for window with id:" + str(id) + " is:" + str(newFactor)
  # and remember the factor
  data[str(id)] = str(newFactor)
  # store info
  if verbose:
    print " Write state to file:  " + str(storageFile)

  with open(storageFile, 'w') as outfile:
    json.dump(data, outfile)

  newPos = calcNewPos(screen, position, newFactor)


else:
  newPos = calcNewPos(screen, position, factor)

flags = wnck.WINDOW_CHANGE_X | wnck.WINDOW_CHANGE_Y | wnck.WINDOW_CHANGE_WIDTH | wnck.WINDOW_CHANGE_HEIGHT
active.unmaximize()

if verbose:
  print "new size " + str(newPos)


# only apply the corrections if the window has window decorations 
gemoetryRaw = active.get_client_window_geometry()
if gemoetryRaw == currentPos:
  # no window decoration discovered this is default for chrome.... 
  active.set_geometry(gravity=newPos[4] ,
                    geometry_mask=flags,
                    x=int(newPos[0]) ,
                    y=int(newPos[1]),
                    width=int(newPos[2]),
                    height=int(newPos[3]))
else:

  active.set_geometry(gravity=newPos[4],
                    geometry_mask=flags,
                    x=int(newPos[0] + correctX),
                    y=int(newPos[1] + correctY),
                    width=int(newPos[2] + correctW),
                    height=int(newPos[3] + correctH))

