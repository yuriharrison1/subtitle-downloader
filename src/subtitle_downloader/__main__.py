#!/usr/bin/env python3
"""
Main entry point for the subtitle downloader package
"""

import sys
import os
from pathlib import Path

from .utils import detect_gui_preference, is_video_file

def main():
    if len(sys.argv) < 2:
        print("Error: No file selected")
        print("Usage: download-subtitle <video-file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    if not is_video_file(file_path):
        print("Error: Please select a valid video file")
        sys.exit(1)
    
    gui_type = detect_gui_preference()
    
    try:
        if gui_type == 'qt':
            from .gui_qt import main_qt
            sys.exit(main_qt(file_path))
        else:
            from .gui_gtk import main_gtk
            sys.exit(main_gtk(file_path))
    except ImportError as e:
        print(f"Error: No GUI backend available - {e}")
        print("Please install PyQt5 or PyGObject")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
