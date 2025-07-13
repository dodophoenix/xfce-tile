"""
Mouse positioning and stateful window management
"""

import json
import os
from Xlib import display
from .config import Config


class MouseController:
    """Handles mouse cursor positioning"""
    
    @staticmethod
    def place_cursor_over_window(window_rect, verbose=False):
        """
        Place mouse cursor over the center of a window
        
        Args:
            window_rect (tuple): Window rectangle (x, y, width, height)
            verbose (bool): Enable debug output
        """
        d = display.Display()
        s = d.screen()
        root = s.root
        
        x = round(window_rect[0] + window_rect[2] / 2)
        y = round(window_rect[1] + window_rect[3] / 2)
        
        if verbose:
            print(f"Moving cursor to window center: {x}, {y}")
        
        root.warp_pointer(x, y)
        d.sync()


class StatefulWindowManager:
    """Manages stateful window sizing with factor cycling"""
    
    def __init__(self, storage_file=None, verbose=False):
        self.storage_file = storage_file or Config.STORAGE_FILE
        self.verbose = verbose
    
    def get_next_factor(self, window_id, factors):
        """
        Get the next scaling factor for a window in stateful mode
        
        Args:
            window_id: Unique window identifier
            factors (list): List of available scaling factors
            
        Returns:
            float: Next scaling factor to use
        """
        if self.verbose:
            print(f"Getting next scale factor for window {window_id}")
        
        # Load existing state
        data = self._load_state()
        
        # Get current factor for this window
        current_factor = data.get(str(window_id), 1.0)
        
        try:
            current_factor = float(current_factor)
        except (ValueError, TypeError):
            current_factor = 1.0
        
        # Find index of current factor
        try:
            current_index = factors.index(current_factor)
        except ValueError:
            current_index = 0  # Default to first factor if not found
        
        # Calculate next factor (cycle through list)
        next_index = (current_index + 1) % len(factors)
        next_factor = factors[next_index]
        
        if self.verbose:
            print(f"  Current factor: {current_factor}")
            print(f"  Next factor: {next_factor}")
        
        # Store new factor
        data[str(window_id)] = str(next_factor)
        self._save_state(data)
        
        return next_factor
    
    def _load_state(self):
        """Load state from storage file"""
        if not os.path.isfile(self.storage_file):
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            if self.verbose:
                print(f"Warning: Could not load state file: {e}")
            return {}
    
    def _save_state(self, data):
        """Save state to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f)
            if self.verbose:
                print(f"Saved state to: {self.storage_file}")
        except IOError as e:
            if self.verbose:
                print(f"Warning: Could not save state file: {e}")


def get_window_id(window):
    """
    Get unique identifier for a window
    
    Args:
        window: WNCK window object
        
    Returns:
        int: Window XID
    """
    return window.get_xid()
