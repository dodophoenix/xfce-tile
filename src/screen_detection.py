"""
Screen and panel detection functionality
"""

import gi
gi.require_version('Gdk', '3.0')
gi.require_version("Wnck", "3.0")

from gi.repository import Gdk, Wnck
from .config import Config


class WorkArea:
    """Simple work area representation"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class ScreenDetector:
    """Handles screen and panel detection"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def discover_screens(self):
        """
        Discover all screens and their work areas (excluding panels)
        
        Returns:
            list: List of screen dictionaries with work area information
        """
        screens = []
        display = Gdk.Display.get_default()
        
        if display is None:
            if self.verbose:
                print("Could not get default display, falling back to hardcoded screen config")
            return Config.DEFAULT_SCREENS
        
        n_monitors = display.get_n_monitors()
        if self.verbose:
            print(f"Found {n_monitors} monitors")
        
        for monitor_idx in range(n_monitors):
            monitor = display.get_monitor(monitor_idx)
            if monitor is None:
                continue
                
            screen_info = self._analyze_monitor(monitor, monitor_idx)
            screens.append(screen_info)
        
        return screens
    
    def _analyze_monitor(self, monitor, monitor_idx):
        """
        Analyze a single monitor for panels and calculate work area
        
        Args:
            monitor: GTK monitor object
            monitor_idx (int): Monitor index
            
        Returns:
            dict: Screen information with work area
        """
        # Get physical monitor geometry
        monitor_geometry = monitor.get_geometry()
        
        # Try to get work area (area not occupied by panels/taskbars)
        work_area = None
        use_fallback = False
        
        try:
            work_area = monitor.get_workarea()
            if self.verbose:
                print(f"  Monitor {monitor_idx + 1}: get_workarea() returned: {work_area.x}x{work_area.y} {work_area.width}x{work_area.height}")
            
            # Check if work area equals monitor area (indicates no panels detected)
            if (work_area.x == monitor_geometry.x and work_area.y == monitor_geometry.y and
                work_area.width == monitor_geometry.width and work_area.height == monitor_geometry.height):
                if self.verbose:
                    print(f"  Monitor {monitor_idx + 1}: get_workarea() found no panels, using fallback detection")
                use_fallback = True
                
        except (AttributeError, Exception) as e:
            if self.verbose:
                print(f"  Monitor {monitor_idx + 1}: get_workarea() failed: {e}, using fallback panel detection")
            use_fallback = True
        
        # Force fallback if GTK didn't detect panels or if work area detection failed
        if work_area is None or use_fallback:
            if self.verbose:
                print(f"  Monitor {monitor_idx + 1}: Using fallback panel detection...")
            work_area = self._detect_panels_manually(monitor_geometry)
        
        name = f"screen-{monitor_idx + 1}"
        
        # Create screen info with both work area and monitor geometry
        screen_info = {
            "name": name,
            "x": work_area.x,
            "y": work_area.y, 
            "width": work_area.width,
            "height": work_area.height,
            # Store original geometry for intersection detection
            "monitor_x": monitor_geometry.x,
            "monitor_y": monitor_geometry.y,
            "monitor_width": monitor_geometry.width,
            "monitor_height": monitor_geometry.height
        }
        
        if self.verbose:
            self._log_screen_info(screen_info, monitor_geometry, work_area)
        
        return screen_info
    
    def _detect_panels_manually(self, monitor_geometry):
        """
        Fallback method to detect XFCE panels using WNCK
        
        Args:
            monitor_geometry: GTK rectangle with monitor dimensions
            
        Returns:
            WorkArea: Calculated work area excluding detected panels
        """
        # Start with full monitor as work area
        work_x = monitor_geometry.x
        work_y = monitor_geometry.y
        work_width = monitor_geometry.width
        work_height = monitor_geometry.height
        
        panels_found = 0
        
        try:
            wnck_screen = Wnck.Screen.get_default()
            if wnck_screen is None:
                if self.verbose:
                    print("    Warning: Could not get Wnck screen for panel detection")
            else:
                wnck_screen.force_update()
                panels_found = self._scan_for_panels(wnck_screen, monitor_geometry, work_x, work_y, work_width, work_height)
                
                # Update work area based on detected panels
                if panels_found > 0:
                    work_x, work_y, work_width, work_height = self._calculate_work_area_from_panels(
                        wnck_screen, monitor_geometry, work_x, work_y, work_width, work_height
                    )
        
        except Exception as e:
            if self.verbose:
                print(f"    Error detecting panels: {e}")
        
        if self.verbose:
            if panels_found > 0:
                print(f"    Final work area: {work_x}x{work_y} {work_width}x{work_height}")
            else:
                print(f"    No panels found - using full monitor: {work_x}x{work_y} {work_width}x{work_height}")
        
        return WorkArea(work_x, work_y, work_width, work_height)
    
    def _scan_for_panels(self, wnck_screen, monitor_geometry, work_x, work_y, work_width, work_height):
        """Scan for panel windows and count them"""
        panels_found = 0
        
        for window in wnck_screen.get_windows():
            if window.get_window_type() == Wnck.WindowType.DOCK:
                geom = window.get_geometry()
                win_x, win_y, win_w, win_h = geom
                
                if self.verbose:
                    print(f"      Found dock window: '{window.get_name()}' at {win_x}x{win_y} {win_w}x{win_h}")
                
                # Check if this panel intersects with our monitor
                if self._panel_intersects_monitor(win_x, win_y, win_w, win_h, monitor_geometry):
                    panels_found += 1
                    if self.verbose:
                        print(f"        Panel intersects with monitor")
                else:
                    if self.verbose:
                        print(f"        Panel does not intersect with monitor")
        
        if self.verbose:
            print(f"    Found {panels_found} panel(s) on this monitor")
        
        return panels_found
    
    def _calculate_work_area_from_panels(self, wnck_screen, monitor_geometry, work_x, work_y, work_width, work_height):
        """Calculate work area by subtracting panel areas"""
        for window in wnck_screen.get_windows():
            if window.get_window_type() == Wnck.WindowType.DOCK:
                geom = window.get_geometry()
                win_x, win_y, win_w, win_h = geom
                
                if self._panel_intersects_monitor(win_x, win_y, win_w, win_h, monitor_geometry):
                    # Determine panel position and adjust work area
                    work_x, work_y, work_width, work_height = self._adjust_work_area_for_panel(
                        win_x, win_y, win_w, win_h, monitor_geometry, work_x, work_y, work_width, work_height
                    )
        
        return work_x, work_y, work_width, work_height
    
    def _panel_intersects_monitor(self, win_x, win_y, win_w, win_h, monitor_geometry):
        """Check if panel window intersects with monitor"""
        return (win_x < monitor_geometry.x + monitor_geometry.width and
                win_x + win_w > monitor_geometry.x and
                win_y < monitor_geometry.y + monitor_geometry.height and
                win_y + win_h > monitor_geometry.y)
    
    def _adjust_work_area_for_panel(self, win_x, win_y, win_w, win_h, monitor_geometry, work_x, work_y, work_width, work_height):
        """Adjust work area based on panel position"""
        # Top panel (within 10px of top edge, spans most of width)
        if (win_y <= monitor_geometry.y + 10 and win_w > monitor_geometry.width * 0.5):
            panel_bottom = win_y + win_h
            if panel_bottom > work_y:
                adjust = panel_bottom - work_y
                work_y += adjust
                work_height -= adjust
                if self.verbose:
                    print(f"        Detected TOP panel: adjusted work_y to {work_y}, work_height to {work_height}")
        
        # Bottom panel (within 10px of bottom edge, spans most of width)
        elif (win_y + win_h >= monitor_geometry.y + monitor_geometry.height - 10 and
              win_w > monitor_geometry.width * 0.5):
            panel_top = win_y
            if panel_top < work_y + work_height:
                old_height = work_height
                work_height = panel_top - work_y
                if self.verbose:
                    print(f"        Detected BOTTOM panel: reduced work_height from {old_height} to {work_height}")
        
        # Left panel (within 10px of left edge, spans most of height)
        elif (win_x <= monitor_geometry.x + 10 and win_h > monitor_geometry.height * 0.5):
            panel_right = win_x + win_w
            if panel_right > work_x:
                adjust = panel_right - work_x
                work_x += adjust
                work_width -= adjust
                if self.verbose:
                    print(f"        Detected LEFT panel: adjusted work_x to {work_x}, work_width to {work_width}")
        
        # Right panel (within 10px of right edge, spans most of height)
        elif (win_x + win_w >= monitor_geometry.x + monitor_geometry.width - 10 and
              win_h > monitor_geometry.height * 0.5):
            panel_left = win_x
            if panel_left < work_x + work_width:
                old_width = work_width
                work_width = panel_left - work_x
                if self.verbose:
                    print(f"        Detected RIGHT panel: reduced work_width from {old_width} to {work_width}")
        else:
            if self.verbose:
                print(f"        Panel position not recognized as standard edge panel")
        
        return work_x, work_y, work_width, work_height
    
    def _log_screen_info(self, screen_info, monitor_geometry, work_area):
        """Log detailed screen information"""
        print(f"  {screen_info['name']}:")
        print(f"    Physical: {monitor_geometry.x}x{monitor_geometry.y} {monitor_geometry.width}x{monitor_geometry.height}")
        print(f"    Work area: {work_area.x}x{work_area.y} {work_area.width}x{work_area.height}")
        
        # Calculate panel positions for debugging
        panels = []
        if work_area.x > monitor_geometry.x:
            panels.append(f"Left panel: {work_area.x - monitor_geometry.x}px")
        if work_area.y > monitor_geometry.y:
            panels.append(f"Top panel: {work_area.y - monitor_geometry.y}px")
        if (monitor_geometry.x + monitor_geometry.width) > (work_area.x + work_area.width):
            panels.append(f"Right panel: {(monitor_geometry.x + monitor_geometry.width) - (work_area.x + work_area.width)}px")
        if (monitor_geometry.y + monitor_geometry.height) > (work_area.y + work_area.height):
            panels.append(f"Bottom panel: {(monitor_geometry.y + monitor_geometry.height) - (work_area.y + work_area.height)}px")
        
        if panels:
            print(f"    Detected panels: {', '.join(panels)}")
        else:
            print(f"    No panels detected")


def find_window_screen(window_x, window_y, window_width, window_height, screens, verbose=False):
    """
    Find which screen contains the most of a window
    
    Args:
        window_x, window_y, window_width, window_height: Window geometry
        screens (list): List of screen dictionaries
        verbose (bool): Enable debug output
        
    Returns:
        dict: Best matching screen information
    """
    if verbose:
        print("Find best matching screen for window:")

    best_match = screens[0]  # Always use a default
    best_percentage = -1000
    
    for screen in screens:
        # Use monitor coordinates for intersection detection (not work area)
        monitor_x = screen.get('monitor_x', screen['x'])
        monitor_y = screen.get('monitor_y', screen['y']) 
        monitor_width = screen.get('monitor_width', screen['width'])
        monitor_height = screen.get('monitor_height', screen['height'])
        
        # Check for intersection
        if not _box_intersects(window_x, window_y, window_x + window_width, window_y + window_height,
                              monitor_x, monitor_y, monitor_x + monitor_width, monitor_y + monitor_height):
            if verbose:
                print(f"  No intersection with: {screen['name']}")
            continue

        # Calculate intersection area
        x1 = max(window_x, monitor_x)
        y1 = max(window_y, monitor_y)
        x2 = min(window_x + window_width, monitor_x + monitor_width)
        y2 = min(window_y + window_height, monitor_y + monitor_height)

        window_area = window_width * window_height
        intersection_area = (x2 - x1) * (y2 - y1)
        percentage_on_screen = intersection_area * 100 / window_area

        if verbose:
            print(f"  {percentage_on_screen:.1f}% are on: {screen['name']}")

        if best_percentage < percentage_on_screen:
            best_percentage = percentage_on_screen
            best_match = screen

    if verbose:
        print(f"  Using: {best_match['name']} as best match")
        print(f"  Screen work area: {best_match['x']}x{best_match['y']} {best_match['width']}x{best_match['height']}")

    return best_match


def _box_intersects(left_a, top_a, right_a, bottom_a, left_b, top_b, right_b, bottom_b):
    """Check if two boxes intersect"""
    return not (left_a > right_b or
                right_a < left_b or
                top_a > bottom_b or
                bottom_a < top_b)
