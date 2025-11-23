"""
Subtitle Downloader - Automatic subtitle downloader with file manager integration
"""

__version__ = "1.0.0"
__author__ = "Yuri Brandao"
__email__ = "yuir.cgdt@gmail.com"

from .core import SubtitleDownloader
from .config import Config
from .utils import is_video_file, get_unique_subtitle_path, detect_gui_preference
from .gui_qt import main_qt
from .gui_gtk import main_gtk

__all__ = [
    'SubtitleDownloader',
    'Config', 
    'is_video_file',
    'get_unique_subtitle_path',
    'detect_gui_preference',
    'main_qt',
    'main_gtk'
]
