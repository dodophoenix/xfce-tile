#!/usr/bin/env python3
"""
XFCE Window Tiling System - Main Application

A clean, modular window tiling system for XFCE desktop environment.
Supports dynamic positioning, multi-monitor setups, and panel-aware tiling.

Usage:
    python main.py -p <position> [options]
    
Examples:
    python main.py -p sw           # Position window in south-west
    python main.py -p e -f 1.5     # Position east with 1.5x scaling
    python main.py -p center -s    # Center with stateful scaling
"""

import sys
import gi

gi.require_version("Wnck", "3.0")
from gi.repository import Wnck

from src.config import Config, parse_arguments, get_factor_list
from src.screen_detection import ScreenDetector, find_window_screen
from src.window_manager import ApplicationDetector, WindowPositioner, GeometryCorrector
from src.utils import MouseController, StatefulWindowManager, get_window_id


class XFCETilingApp:
    """Main application class for XFCE window tiling"""
    
    def __init__(self):
        self.args = None
        self.verbose = False
        self.screen_detector = None
        self.window_positioner = None
        self.stateful_manager = None
        
    def run(self):
        """Main application entry point"""
        try:
            # Parse arguments
            self.args = parse_arguments()
            self.verbose = self.args.verbose
            
            # Initialize components
            self._initialize_components()
            
            # Validate environment
            if not self._validate_environment():
                return 1
            
            # Get active window and screen information
            active_window, current_geometry, target_screen = self._get_window_info()
            
            # Analyze application type
            app_info = ApplicationDetector.analyze_window(active_window)
            self._log_window_info(active_window, app_info)
            
            # Determine scaling factor
            factor = self._determine_scaling_factor(active_window)
            
            # Calculate new position
            new_position = self._calculate_new_position(
                target_screen, active_window, current_geometry, factor, app_info
            )
            
            # Apply new position
            self._apply_window_position(active_window, new_position, app_info)
            
            # Move cursor if requested
            if self.args.move_cursor:
                self._move_cursor_to_window(new_position)
            
            return 0
            
        except KeyboardInterrupt:
            if self.verbose:
                print("Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _initialize_components(self):
        """Initialize application components"""
        self.screen_detector = ScreenDetector(verbose=self.verbose)
        self.window_positioner = WindowPositioner(verbose=self.verbose)
        
        if self.args.stateful:
            self.stateful_manager = StatefulWindowManager(verbose=self.verbose)
    
    def _validate_environment(self):
        """Validate that we're running in a suitable environment"""
        wnck_screen = Wnck.Screen.get_default()
        if wnck_screen is None:
            print("Error: No X11 display found. This script requires XFCE/X11 environment.")
            print("Make sure you're running this on a system with XFCE desktop environment.")
            return False
        return True
    
    def _get_window_info(self):
        """Get active window and determine target screen"""
        # Get window manager screen
        wnck_screen = Wnck.Screen.get_default()
        wnck_screen.force_update()
        
        # Get active window
        active_window = wnck_screen.get_active_window()
        if active_window is None:
            raise RuntimeError("No active window found")
        
        # Get current window geometry
        current_geometry = active_window.get_geometry()
        
        # Discover screens and find target screen
        if Config.AUTO_DISCOVER_SCREENS:
            screens = self.screen_detector.discover_screens()
        else:
            screens = Config.DEFAULT_SCREENS
        
        target_screen = find_window_screen(
            max(0, current_geometry[0]), max(0, current_geometry[1]),
            current_geometry[2], current_geometry[3],
            screens, verbose=self.verbose
        )
        
        return active_window, current_geometry, target_screen
    
    def _log_window_info(self, window, app_info):
        """Log window and application information"""
        if self.verbose:
            print(f"Active window: {app_info['window_name']}")
            print(f"Application: {app_info['app_name']}")
            print(f"Class: {app_info['window_class']}")
            print(f"Is terminal: {app_info['is_terminal']}")
    
    def _determine_scaling_factor(self, window):
        """Determine the scaling factor to use"""
        if self.args.stateful:
            # Get factors list and cycle to next factor
            factors = get_factor_list(self.args.custom_factors)
            window_id = get_window_id(window)
            factor = self.stateful_manager.get_next_factor(window_id, factors)
        else:
            # Use specified factor
            factor = self.args.factor
        
        if self.verbose:
            print(f"Using scaling factor: {factor}")
        
        return factor
    
    def _calculate_new_position(self, screen, window, current_geometry, factor, app_info):
        """Calculate new window position"""
        # Get window decoration geometry for corrections
        geometry_raw = window.get_client_window_geometry()
        
        # Calculate new position
        new_position = self.window_positioner.calculate_position(
            screen=screen,
            position=self.args.position,
            factor=factor,
            current_geometry=current_geometry,
            vertical_only=self.args.vertical_only,
            horizontal_only=self.args.horizontal_only
        )
        
        if self.verbose:
            print(f"New geometry calculated: {new_position}")
        
        return new_position
    
    def _apply_window_position(self, window, new_position, app_info):
        """Apply the calculated position to the window"""
        # Unmaximize window first
        window.unmaximize()
        
        # Get current and raw geometry for corrections
        current_geometry = window.get_geometry()
        geometry_raw = window.get_client_window_geometry()
        
        # Calculate geometry corrections
        correction_x, correction_y = GeometryCorrector.calculate_corrections(
            geometry_raw, current_geometry, app_info, self.args.position, self.verbose
        )
        
        # Apply geometry with corrections
        flags = (Wnck.WindowMoveResizeMask.X | Wnck.WindowMoveResizeMask.Y | 
                Wnck.WindowMoveResizeMask.WIDTH | Wnck.WindowMoveResizeMask.HEIGHT)
        
        window.set_geometry(
            gravity=new_position[4],
            geometry_mask=flags,
            x=round(new_position[0] - correction_x),
            y=round(new_position[1] - correction_y),
            width=round(new_position[2]),
            height=round(new_position[3])
        )
        
        if self.verbose:
            print(f"Applied geometry: x={round(new_position[0] - correction_x)}, "
                  f"y={round(new_position[1] - correction_y)}, "
                  f"w={round(new_position[2])}, h={round(new_position[3])}")
    
    def _move_cursor_to_window(self, new_position):
        """Move cursor to window center if requested"""
        # Calculate window rectangle with corrections
        current_geometry = Wnck.Screen.get_default().get_active_window().get_geometry()
        geometry_raw = Wnck.Screen.get_default().get_active_window().get_client_window_geometry()
        
        correction_x = geometry_raw[0] - current_geometry[0]
        correction_y = geometry_raw[1] - current_geometry[1]
        
        # Keep window above others temporarily
        window = Wnck.Screen.get_default().get_active_window()
        window.make_above()
        window.unmake_above()
        
        # Move cursor
        window_rect = (
            round(new_position[0] - correction_x),
            round(new_position[1] - correction_y),
            round(new_position[2]),
            round(new_position[3])
        )
        
        MouseController.place_cursor_over_window(window_rect, self.verbose)


def main():
    """Application entry point"""
    app = XFCETilingApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
