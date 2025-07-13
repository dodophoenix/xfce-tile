"""
Configuration and command-line argument parsing
"""

import argparse
from argparse import RawTextHelpFormatter


class Config:
    """Configuration constants and settings"""
    
    # Default screen configuration (fallback when auto-discovery fails)
    DEFAULT_SCREENS = [
        {"name": "screen1", "x": 0, "y": 0, "width": 2560, "height": 1440 - 32},
        {"name": "screen2", "x": 2560, "y": 0, "width": 2560, "height": 1440},
        {"name": "screen3", "x": 2560 + 2560, "y": 0, "width": 1280, "height": 1024}
    ]
    
    # Enable automatic screen discovery
    AUTO_DISCOVER_SCREENS = True
    
    # Storage file for stateful window sizing
    STORAGE_FILE = "/tmp/pywin.json"
    
    # Valid positioning choices
    POSITION_CHOICES = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
    
    # Default scaling factors for stateful mode
    DEFAULT_FACTORS = "1,1.334,1.5,2,3,4"
    
    # Terminal application detection keywords
    TERMINAL_KEYWORDS = ['terminal', 'xterm', 'konsole', 'gnome-terminal']
    
    # Terminal-specific positioning corrections (in pixels)
    TERMINAL_CORRECTIONS = {
        'bottom_positions': -2,  # For s, sw, se positions
        'right_positions': -1,   # For e, ne, se positions
    }


def parse_arguments():
    """
    Parse command-line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='XFCE Window Tiling - Position and tile windows using dynamic grid',
        formatter_class=RawTextHelpFormatter
    )
    
    parser.add_argument(
        '-p', '--pos', 
        dest='position', 
        metavar="position", 
        required=True, 
        choices=Config.POSITION_CHOICES,
        help=f'Direction to place window. Using abbreviations for directions like n=north ne=northeast and so on. Use one of: {",".join(Config.POSITION_CHOICES)}'
    )
    
    parser.add_argument(
        '-f', '--factor', 
        dest='factor', 
        metavar="factor", 
        type=float, 
        default=2,
        help='Default scale factor'
    )
    
    parser.add_argument(
        '-s', '--stateful', 
        dest='stateful', 
        action='store_true',
        help=f'Remember window sizing by storing data in: {Config.STORAGE_FILE}'
    )
    
    parser.add_argument(
        '-v', '--verbose', 
        dest='verbose', 
        action='store_true',
        help='Print debugging output'
    )
    
    parser.add_argument(
        '-o', '--horizontal', 
        dest='horizontal_only', 
        action='store_true',
        help='Scale only horizontal direction'
    )
    
    parser.add_argument(
        '-e', '--vertically', 
        dest='vertical_only', 
        action='store_true',
        help='Scale only vertical direction'
    )
    
    parser.add_argument(
        '-c', '--with-cursor', 
        dest='move_cursor', 
        action='store_true', 
        default=False,
        help='Place mouse cursor over moved window. Subsequent invocations should address same window if system activates windows on hover'
    )
    
    parser.add_argument(
        '-m', '--my-factors', 
        dest='custom_factors', 
        metavar="scale-factors", 
        default=Config.DEFAULT_FACTORS,
        help='Comma delimited list of scale-factors to use. e.g. "1,1.5,2,3" This requires stateful option.'
    )
    
    return parser.parse_args()


def get_factor_list(factor_string):
    """
    Parse factor string into list of floats
    
    Args:
        factor_string (str): Comma-separated factor values
        
    Returns:
        list: List of float factors
    """
    factors = []
    for elem in factor_string.split(","):
        try:
            factors.append(float(elem.strip()))
        except ValueError:
            continue
    return factors if factors else [1, 2]  # Fallback to basic factors
