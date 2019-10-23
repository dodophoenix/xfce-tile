#!/usr/bin/env bash

BASE=`dirname "$(readlink -f "$0")"`

PYWIN="${BASE}/pywin.py"

xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_1" -s "python ${PYWIN} -s -p sw" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_2" -s "python ${PYWIN} -s -p s" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_3" -s "python ${PYWIN} -s -p se" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_4" -s "python ${PYWIN} -s -p w" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_5" -s "python ${PYWIN} -s -p center" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_6" -s "python ${PYWIN} -s -p e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_7" -s "python ${PYWIN} -s -p nw" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_8" -s "python ${PYWIN} -s -p n"  --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_9" -s "python ${PYWIN} -s -p ne" --create -t string

