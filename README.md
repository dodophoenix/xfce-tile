# xfce-tile
placement / tile xfce windows using dynamic grid


# getting started 

* download the script
* edit screens on top of the file
* add keyboard shortcuts to xfce e.g.: 

```
    Alt + Num - 4 > pywin.py --position w --stateful 
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
  -s, --stateful        remember window sizing by storing some data under in: /tmp/pywin.json
  -v, --verbose         print some debugging output
  -m scale-factors, --my-factors scale-factors
                        Comma delimited list of scale-factors to use. e.g. "1,1.5,2,3" This requires stateful option to work.
