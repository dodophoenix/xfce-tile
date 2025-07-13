#!/usr/bin/env python3
"""
Backward compatibility wrapper for pywin.py
Maintains compatibility with existing keyboard shortcuts and usage patterns.
"""

from main import main
import sys

if __name__ == "__main__":
    sys.exit(main())
