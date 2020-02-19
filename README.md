# xfce-tile
placement / tile xfce windows using dynamic grid


# getting started 

* checkout or download the script
* install required python3 and GObject module for python  
```
# ubuntu
apt-get install python3-gi
# arch 
pacman -S python-gobject
```  

* Add keyboard shortcuts to xfce.\
 Using the  `xfce-setup-shortcuts.sh`-script will add all shortcuts.\
 You may manually add shortcuts using xfce4-keyboard-settings.\
  e.g. Link Alt + Num -4 to the pywin command. \
```
    Alt + Num - 4 > python /some/path/pywin.py --position w --stateful 
```


# usage
```
usage: pywin.py [-h] -p position [-f factor] [-s] [-v] [-m scale-factors]

Window-Placement/Window-tiling

optional arguments:
  -h, --help            show this help message and exit
  -p position, --pos position
                        Direction to place window. Using abbreviations for directions like n=north ne=northeast and so on. Use one of:n,ne,e,se,s,sw,w,nw,center
  -f factor, --factor factor
                        default scale factor 
  -s, --stateful        remember window sizing by storing some data under: /tmp/pywin.json
  -v, --verbose         print some debugging output
  -o, --horizontal      scale only horizontal
  -e, --vertically      scale only vertical
  -m scale-factors, --my-factors scale-factors
                        Comma delimited list of scale-factors to use. e.g. "1,1.5,2,3" This requires stateful option.
