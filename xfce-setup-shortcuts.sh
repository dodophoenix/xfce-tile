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

xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_1" -s "python ${PYWIN} -s -p sw -o" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_3" -s "python ${PYWIN} -s -p se -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_7" -s "python ${PYWIN} -s -p nw -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_5" -s "python ${PYWIN} -s -p center -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_7" -s "python ${PYWIN} -s -p nw -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_9" -s "python ${PYWIN} -s -p ne -o" --create -t string

xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_1" -s "python ${PYWIN} -s -p sw -e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_3" -s "python ${PYWIN} -s -p se -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_7" -s "python ${PYWIN} -s -p nw -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_5" -s "python ${PYWIN} -s -p center -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_7" -s "python ${PYWIN} -s -p nw -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_9" -s "python ${PYWIN} -s -p ne -e" --create -t string