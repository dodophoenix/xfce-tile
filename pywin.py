#!/usr/bin/env python
# coding: utf8
import argparse
import gtk
import json
import os
import wnck
from argparse import RawTextHelpFormatter

storageFile="/tmp/pywin.json"

choices = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw','maximize']

# correcting miscalculations this might be related to decorations of the window-manager
#
correctY = -32
correctX = -2
correctW = 0
correctH = 0

# defines the screens and their positions. TODO: read them from somewhere from system
screens = [
  {"name": "screen1", "x": 0, "y": 0, "width": 2560, "height": 1440},
  {"name": "screen2", "x": 2560, "y": 0, "width": 2560, "height": 1440},
  {"name": "screen3", "x": 2560 + 2560, "y": 0, "width": 1280, "height": 1024}
]


def findBounds(x, y):
  print "x:" + str(x) + " y:" + str(y)
  for screen in screens:
    if x >= screen['x'] and x < (screen['x'] + screen['width']) and y >= screen['y'] and y < (screen['y'] + screen['height']):
      return screen
  return None


def read_args():
  parser = argparse.ArgumentParser(description='Window-Placement', formatter_class=RawTextHelpFormatter)
  parser.add_argument('-p', '--pos', dest='position', metavar="position", required=True, choices=choices,
                      help='Position. Gemäß Himmelsrichtungen n=north ne=Northeast usw. Eine Position aus:'+
                           (','.join(choices)))

  parser.add_argument('-f', '--factor', dest='factor', metavar="factor", type=int,default=2,
                      help='Skalierungsfaktor (halbierung 2, drittelung 3).')

  parser.add_argument('-s', '--stateful', dest='stateful', action='store_true',
                      help='Erinnert sich an Fenstergößen und erlaubt mehr Magic')

  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                      help='some more output ')

  parser.add_argument('-m', '--my-factors', dest='myfactor', metavar="position", default="1,1.5,2,3",
                      help='Comma delimited list of scalefactors to use. requires stateful option')

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

  if position == 'maximize':
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


# rauskriegen auf welchem screen das Fenster positioniert werden soll
screen = findBounds(max(0, winX), max(0, winY))

if verbose:
  print "current window lives on scree " + str(screen["name"]) + " defined as:"+ str(screen)



if(stateful):
  if verbose:
    print "read scale factor from file" + storageFile
  # gespeicherte daten lesen
  # aktuellen skaölierungs faktor raussuchen
  # neuen faktor berechnen
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
    print "next scale-factor for window with id " + str(id) + " is:" + str(newFactor)
  # and remember the factor
  data[str(id)] = str(newFactor)
  # store info
  if verbose:
    print "write state to file:  " + str(storageFile)

  with open(storageFile, 'w') as outfile:
    json.dump(data, outfile)

  newPos = calcNewPos(screen, position, newFactor)


else:
  newPos = calcNewPos(screen, position, factor)

flags = wnck.WINDOW_CHANGE_X | wnck.WINDOW_CHANGE_Y | wnck.WINDOW_CHANGE_WIDTH | wnck.WINDOW_CHANGE_HEIGHT
active.unmaximize()

if verbose:
  print "activate new size " + str(newPos) + " also adding additionals"


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

