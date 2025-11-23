#!/usr/bin/env python3
"""
Thin wrapper for the subtitle downloader package
Command-line interface for subtitle downloading
"""

import sys
import os

# Add the package to Python path
package_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(package_dir))

from subtitle_downloader.__main__ import main

if __name__ == "__main__":
    main()
