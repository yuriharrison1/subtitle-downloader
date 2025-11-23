import os
import subprocess
from pathlib import Path

# Supported video extensions
VIDEO_EXTENSIONS = {
    '.avi', '.mkv', '.mp4', '.mov', '.wmv', '.webm', '.flv', '.3gp', 
    '.m4v', '.mpg', '.mpeg', '.vob', '.ogv', '.ts', '.m2ts', '.divx',
    '.m4v', '.mpg', '.mpe', '.mpv', '.qt', '.asf', '.ogm', '.dv'
}

def is_video_file(file_path):
    """Checks if file is a common video file"""
    path = Path(file_path)
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS

def get_unique_subtitle_path(video_path, language):
    """Generates a unique filename for the subtitle"""
    video_stem = Path(video_path).stem
    base_name = f"{video_stem}.{language}.srt"
    base_path = Path(video_path).parent / base_name
    
    if not base_path.exists():
        return base_path
    
    counter = 1
    while True:
        new_name = f"{video_stem}.{language}_{counter}.srt"
        new_path = Path(video_path).parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def detect_gui_preference():
    """Detects which GUI to use based on environment"""
    desktop_session = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    
    # Check if pcmanfm-qt is in use
    try:
        result = subprocess.run(['pgrep', '-f', 'pcmanfm-qt'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            return 'qt'
    except:
        pass
    
    # Heuristic based on desktop environment
    if 'qt' in desktop_session or 'kde' in desktop_session:
        return 'qt'
    elif 'gtk' in desktop_session or 'xfce' in desktop_session or 'gnome' in desktop_session:
        return 'gtk'
    elif session_type == 'wayland':
        return 'gtk'
    else:
        # Try to import to see which is available
        try:
            from PyQt5.QtWidgets import QApplication
            return 'qt'
        except ImportError:
            try:
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                return 'gtk'
            except ImportError:
                return 'qt'  # Default to Qt

def show_notification(title, message, timeout=5000):
    """Shows a desktop notification"""
    try:
        subprocess.run([
            "notify-send", 
            "-t", str(timeout),
            title,
            message
        ], check=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback to terminal output if notify-send fails
        print(f"{title}: {message}")
