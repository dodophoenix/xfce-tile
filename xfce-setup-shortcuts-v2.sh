#!/usr/bin/env bash
#
# XFCE Keyboard Shortcuts Setup - Updated for Clean Architecture
# 
# This script sets up keyboard shortcuts for the modular XFCE-Tile system.
# Uses the new main.py entry point while maintaining backward compatibility.
#

BASE=`dirname "$(readlink -f "$0")"`

# Use the new modular main.py entry point
MAIN_SCRIPT="${BASE}/main.py"

# Fallback to legacy pywin.py if main.py doesn't exist
if [ ! -f "$MAIN_SCRIPT" ]; then
    MAIN_SCRIPT="${BASE}/pywin.py"
    echo "Warning: Using legacy pywin.py - consider upgrading to modular version"
fi

# Additional parameters to modify behavior
PARAMS="-s --with-cursor"

echo "Setting up XFCE keyboard shortcuts..."
echo "Using script: $MAIN_SCRIPT"
echo "Parameters: $PARAMS"
echo

# Remove existing custom commands
while IFS= read -r line; do
    echo "Removing custom command for $line"
    xfconf-query -c xfce4-keyboard-shortcuts -p "${line}" --reset 2>/dev/null;
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

echo
echo "Setting up new keyboard shortcuts..."

# Basic directional positioning (Alt + Numpad)
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_1" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p sw" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_2" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p s" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_3" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p se" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_4" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p w" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_5" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p center" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_6" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_7" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p nw" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_8" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p n" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Alt>KP_9" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p ne" --create -t string

# Horizontal-only scaling (Ctrl+Super+Alt + Numpad)
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_1" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p sw -o" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_3" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p se -o" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_7" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p nw -o" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_5" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p center -o" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Ctrl><Super><Alt>KP_9" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p ne -o" --create -t string

# Vertical-only scaling (Super+Alt + Numpad)
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_1" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p sw -e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_3" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p se -e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_7" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p nw -e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_5" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p center -e" --create -t string
xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Super><Alt>KP_9" -s "python3 ${MAIN_SCRIPT} ${PARAMS} -p ne -e" --create -t string

echo
echo "✅ Keyboard shortcuts setup completed!"
echo
echo "📋 Shortcut Layout (Numpad):"
echo "   7 (NW)  8 (N)   9 (NE)"
echo "   4 (W)   5 (C)   6 (E) "
echo "   1 (SW)  2 (S)   3 (SE)"
echo
echo "🎮 Key Combinations:"
echo "   Alt + Numpad           = Basic positioning"
echo "   Ctrl+Super+Alt + Numpad = Horizontal-only scaling"
echo "   Super+Alt + Numpad      = Vertical-only scaling"
echo
echo "🎯 Features:"
echo "   - Stateful scaling (-s): Cycles through size factors"
echo "   - Cursor movement (-c): Moves mouse to window center"
echo "   - Panel-aware: Respects taskbars on all sides"
echo "   - Multi-monitor: Works across multiple screens"
echo "   - Terminal-optimized: Special handling for terminal apps"
echo
echo "🚀 Test with: Alt + Numpad 5 (center window)"
