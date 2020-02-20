#!/usr/bin/env bash

BASE=`dirname "$(readlink -f "$0")"`

PYWIN="${BASE}/pywin.py"

# adjust additional params to modifiy the behaviour
PARAMS="-s --with-cursor"

while IFS= read -r line; do
    echo "remove custom command for $line"
    xfconf-query -c xfce4-keyboard-shortcuts -p "${line}" --reset;
done<<'EOF'
/commands/custom/<Alt>KP_1
/commands/custom/<Alt>KP_2
/commands/custom/<Alt>KP_3
/commands/custom/<Alt>KP_4
/commands/custom/<Alt>KP_5
/commands/custom/<Alt>KP_6
/commands/custom/<Alt>KP_7
/commands/custom/<Alt>KP_8
/commands/custom/<Alt>KP_9
/commands/custom/<Ctrl><Super><Alt>KP_1
/commands/custom/<Ctrl><Super><Alt>KP_3
/commands/custom/<Ctrl><Super><Alt>KP_5
/commands/custom/<Ctrl><Super><Alt>KP_7
/commands/custom/<Ctrl><Super><Alt>KP_9
/commands/custom/<Super><Alt>KP_1
/commands/custom/<Super><Alt>KP_3
/commands/custom/<Super><Alt>KP_5
/commands/custom/<Super><Alt>KP_7
/commands/custom/<Super><Alt>KP_9
EOF


xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_1" -s "python ${PYWIN} ${PARAMS} -p sw" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_2" -s "python ${PYWIN} ${PARAMS} -p s" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_3" -s "python ${PYWIN} ${PARAMS} -p se" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_4" -s "python ${PYWIN} ${PARAMS} -p w" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_5" -s "python ${PYWIN} ${PARAMS} -p center" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_6" -s "python ${PYWIN} ${PARAMS} -p e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_7" -s "python ${PYWIN} ${PARAMS} -p nw" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_8" -s "python ${PYWIN} ${PARAMS} -p n"  --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_9" -s "python ${PYWIN} ${PARAMS} -p ne" --create -t string

xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_1" -s "python ${PYWIN} ${PARAMS} -p sw -o" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_3" -s "python ${PYWIN} ${PARAMS} -p se -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_7" -s "python ${PYWIN} ${PARAMS} -p nw -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_5" -s "python ${PYWIN} ${PARAMS} -p center -o" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_9" -s "python ${PYWIN} ${PARAMS} -p ne -o" --create -t string

xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_1" -s "python ${PYWIN} ${PARAMS} -p sw -e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_3" -s "python ${PYWIN} ${PARAMS} -p se -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_7" -s "python ${PYWIN} ${PARAMS} -p nw -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_5" -s "python ${PYWIN} ${PARAMS} -p center -e" --create  -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_9" -s "python ${PYWIN} ${PARAMS} -p ne -e" --create -t string