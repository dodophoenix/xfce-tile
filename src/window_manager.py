"""
Application detection and window management
"""

import gi
gi.require_version("Wnck", "3.0")
from gi.repository import Wnck
from .config import Config


class ApplicationDetector:
    """Detects application types for specific handling"""
    
    @staticmethod
    def analyze_window(window):
        """
        Analyze window to determine application type and properties
        
        Args:
            window: WNCK window object
            
        Returns:
            dict: Window analysis results
        """
        app_name = ""
        window_class = ""
        
        try:
            if window.get_application():
                app_name = window.get_application().get_name().lower()
            if window.get_class_group_name():
                window_class = window.get_class_group_name().lower()
        except:
            pass
        
        is_terminal = any(term in app_name or term in window_class 
                         for term in Config.TERMINAL_KEYWORDS)
        
        return {
            'app_name': app_name,
            'window_class': window_class,
            'is_terminal': is_terminal,
            'window_name': window.get_name() or "Unknown"
        }


class WindowPositioner:
    """Handles window positioning calculations"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def calculate_position(self, screen, position, factor, current_geometry, 
                          vertical_only=False, horizontal_only=False):
        """
        Calculate new window position and size
        
        Args:
            screen (dict): Screen information with work area
            position (str): Target position (n, ne, e, se, s, sw, w, nw, center)
            factor (float): Scaling factor
            current_geometry (tuple): Current window geometry (x, y, width, height)
            vertical_only (bool): Scale only vertically
            horizontal_only (bool): Scale only horizontally
            
        Returns:
            tuple: (x, y, width, height, gravity)
        """
        gravity = Wnck.WindowGravity.NORTHWEST
        
        # Work area coordinates (already exclude panels)
        work_x = screen["x"]
        work_y = screen["y"] 
        work_width = screen["width"]
        work_height = screen["height"]
        
        if self.verbose:
            print(f"calcNewPos: Using work area {work_x}x{work_y} {work_width}x{work_height} "
                  f"for position '{position}' with factor {factor}")
        
        # Calculate dimensions with proper rounding
        if factor == 1.0:
            # For 100%, use exact dimensions to avoid rounding issues
            calc_width = work_width
            calc_height = work_height
        else:
            calc_width = round(work_width / factor)
            calc_height = round(work_height / factor)
        
        # Calculate position based on target location
        position_methods = {
            'n': self._position_north,
            'ne': self._position_northeast,
            'e': self._position_east,
            'se': self._position_southeast,
            's': self._position_south,
            'sw': self._position_southwest,
            'w': self._position_west,
            'nw': self._position_northwest,
            'center': self._position_center
        }
        
        if position not in position_methods:
            raise ValueError(f"Unknown position: {position}")
        
        x, y, width, height = position_methods[position](
            work_x, work_y, work_width, work_height, calc_width, calc_height,
            current_geometry, horizontal_only, vertical_only
        )
        
        if self.verbose:
            right_edge = x + width
            bottom_edge = y + height
            print(f"  Calculated: x={x}, y={y}, w={width}, h={height}")
            print(f"  Right edge: {right_edge}, Bottom edge: {bottom_edge}")
            print(f"  Work area right: {work_x + work_width}, Work area bottom: {work_y + work_height}")
        
        return (x, y, width, height, gravity)
    
    def _position_north(self, work_x, work_y, work_width, work_height, 
                       calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at top, full width"""
        return work_x, work_y, work_width, calc_height
    
    def _position_northeast(self, work_x, work_y, work_width, work_height, 
                           calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at top-right corner"""
        width = calc_width
        height = calc_height
        y = work_y
        x = work_x + work_width - width
        
        if horizontal_only:
            width = calc_width
            height = current_geometry[3]
        if vertical_only:
            width = current_geometry[2]
            height = calc_height
            x = current_geometry[0]
        
        return x, y, width, height
    
    def _position_east(self, work_x, work_y, work_width, work_height,
                      calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at right edge, full height"""
        width = calc_width
        y = work_y
        x = work_x + work_width - width
        height = work_height
        return x, y, width, height
    
    def _position_southeast(self, work_x, work_y, work_width, work_height,
                           calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at bottom-right corner"""
        width = calc_width
        height = calc_height
        y = work_y + work_height - height
        x = work_x + work_width - width
        
        if horizontal_only:
            width = calc_width
            height = current_geometry[3]
            x = work_x + work_width - width
            y = work_y + work_height - current_geometry[3]
        if vertical_only:
            x = current_geometry[0]
            width = current_geometry[2]
            height = calc_height
        
        return x, y, width, height
    
    def _position_south(self, work_x, work_y, work_width, work_height,
                       calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at bottom, full width"""
        height = calc_height
        y = work_y + work_height - height
        x = work_x
        width = work_width
        return x, y, width, height
    
    def _position_southwest(self, work_x, work_y, work_width, work_height,
                           calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at bottom-left corner"""
        width = calc_width
        height = calc_height
        x = work_x
        y = work_y + work_height - height
        
        if horizontal_only:
            width = calc_width
            height = current_geometry[3]
            y = work_y + work_height - current_geometry[3]
        if vertical_only:
            width = current_geometry[2]
            height = calc_height
        
        return x, y, width, height
    
    def _position_west(self, work_x, work_y, work_width, work_height,
                      calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at left edge, full height"""
        width = calc_width
        y = work_y
        x = work_x
        height = work_height
        return x, y, width, height
    
    def _position_northwest(self, work_x, work_y, work_width, work_height,
                           calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at top-left corner"""
        width = calc_width
        height = calc_height
        y = work_y
        x = work_x
        
        if horizontal_only:
            width = calc_width
            height = current_geometry[3]
        if vertical_only:
            width = current_geometry[2]
            height = calc_height
        
        return x, y, width, height
    
    def _position_center(self, work_x, work_y, work_width, work_height,
                        calc_width, calc_height, current_geometry, horizontal_only, vertical_only):
        """Position window at center, specified width, full height"""
        width = calc_width
        height = work_height
        y = work_y
        x = work_x + (work_width - width) // 2
        return x, y, width, height


class GeometryCorrector:
    """Handles window decoration corrections"""
    
    @staticmethod
    def calculate_corrections(geometry_raw, current_geometry, app_info, position, verbose=False):
        """
        Calculate geometry corrections for window decorations and app-specific issues
        
        Args:
            geometry_raw (tuple): Raw window geometry
            current_geometry (tuple): Current window geometry  
            app_info (dict): Application analysis results
            position (str): Target position
            verbose (bool): Enable debug output
            
        Returns:
            tuple: (correction_x, correction_y)
        """
        # Basic window decoration corrections
        correction_x = geometry_raw[0] - current_geometry[0]
        correction_y = geometry_raw[1] - current_geometry[1]
        
        # Apply terminal-specific corrections
        if app_info['is_terminal']:
            terminal_correction_x, terminal_correction_y = GeometryCorrector._get_terminal_corrections(position)
            
            if verbose:
                print(f"Terminal corrections: x={terminal_correction_x}, y={terminal_correction_y}")
            
            correction_x += terminal_correction_x
            correction_y += terminal_correction_y
        
        if verbose:
            print(f"Final corrections: x={correction_x}, y={correction_y}")
        
        return correction_x, correction_y
    
    @staticmethod
    def _get_terminal_corrections(position):
        """
        Get terminal-specific positioning corrections
        
        Args:
            position (str): Target position
            
        Returns:
            tuple: (correction_x, correction_y)
        """
        correction_x = 0
        correction_y = 0
        
        # For bottom-aligned positions, terminals often need adjustment
        if position in ['s', 'sw', 'se']:
            correction_y = Config.TERMINAL_CORRECTIONS['bottom_positions']
        
        # For right-aligned positions, terminals might need adjustment  
        if position in ['e', 'ne', 'se']:
            correction_x = Config.TERMINAL_CORRECTIONS['right_positions']
        
        return correction_x, correction_y
