#!/usr/bin/env python3
"""
Tests for utility functions
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the package to Python path
package_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(package_dir))

from subtitle_downloader.utils import (
    is_video_file, 
    get_unique_subtitle_path, 
    detect_gui_preference,
    show_notification
)

class TestUtils(unittest.TestCase):
    
    def test_video_extensions_comprehensive(self):
        """Test all supported video extensions"""
        test_cases = [
            # Supported extensions
            ('video.mp4', True),
            ('movie.mkv', True),
            ('film.avi', True),
            ('show.mov', True),
            ('clip.wmv', True),
            ('demo.webm', True),
            ('test.flv', True),
            ('mobile.3gp', True),
            ('hd.m4v', True),
            ('dvd.mpg', True),
            ('old.mpeg', True),
            ('vhs.vob', True),
            ('stream.ogv', True),
            ('broadcast.ts', True),
            ('bluray.m2ts', True),
            ('xvid.divx', True),
            ('quicktime.qt', True),
            ('windows.asf', True),
            ('ogg.ogm', True),
            ('digital.dv', True),
            
            # Case sensitivity
            ('VIDEO.MP4', True),
            ('Movie.Mkv', True),
            
            # Unsupported extensions
            ('document.pdf', False),
            ('image.jpg', False),
            ('audio.mp3', False),
            ('text.txt', False),
            ('subtitle.srt', False),
            ('script.py', False),
            ('data.json', False),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                self.assertEqual(is_video_file(filename), expected)
    
    def test_get_unique_subtitle_path_sequence(self):
        """Test subtitle path generation with multiple files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, 'test_movie.mp4')
            Path(video_path).touch()
            
            # Test sequence of subtitle files
            paths_created = []
            
            for i in range(5):
                sub_path = get_unique_subtitle_path(video_path, 'en')
                paths_created.append(sub_path)
                
                # Create the file to force next one to be different
                Path(sub_path).touch()
            
            # Verify all paths are unique
            self.assertEqual(len(set(paths_created)), 5)
            
            # Verify naming pattern
            expected_names = [
                'test_movie.en.srt',
                'test_movie.en_1.srt', 
                'test_movie.en_2.srt',
                'test_movie.en_3.srt',
                'test_movie.en_4.srt'
            ]
            
            for i, path in enumerate(paths_created):
                self.assertEqual(Path(path).name, expected_names[i])
    
    def test_detect_gui_preference(self):
        """Test GUI preference detection"""
        # Mock environment variables for different desktop environments
        
        # Test KDE/Qt environment
        with patch.dict('os.environ', {
            'XDG_CURRENT_DESKTOP': 'KDE',
            'XDG_SESSION_TYPE': 'x11'
        }):
            preference = detect_gui_preference()
            self.assertEqual(preference, 'qt')
        
        # Test GNOME/GTK environment
        with patch.dict('os.environ', {
            'XDG_CURRENT_DESKTOP': 'GNOME',
            'XDG_SESSION_TYPE': 'x11' 
        }):
            preference = detect_gui_preference()
            self.assertEqual(preference, 'gtk')
        
        # Test XFCE/GTK environment
        with patch.dict('os.environ', {
            'XDG_CURRENT_DESKTOP': 'XFCE',
            'XDG_SESSION_TYPE': 'x11'
        }):
            preference = detect_gui_preference()
            self.assertEqual(preference, 'gtk')
        
        # Test Wayland session
        with patch.dict('os.environ', {
            'XDG_CURRENT_DESKTOP': 'GNOME',
            'XDG_SESSION_TYPE': 'wayland'
        }):
            preference = detect_gui_preference()
            self.assertEqual(preference, 'gtk')
    
    @patch('subtitle_downloader.utils.subprocess.run')
    def test_show_notification_success(self, mock_subprocess):
        """Test notification display success"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Should not raise an exception
        show_notification('Test Title', 'Test Message')
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args[0], 'notify-send')
        self.assertEqual(call_args[1], '-t')
        self.assertEqual(call_args[2], '5000')
        self.assertEqual(call_args[3], 'Test Title')
        self.assertEqual(call_args[4], 'Test Message')
    
    @patch('subtitle_downloader.utils.subprocess.run')
    def test_show_notification_fallback(self, mock_subprocess):
        """Test notification fallback to print"""
        mock_subprocess.side_effect = FileNotFoundError()
        
        # Should fallback to print (capture output)
        with patch('builtins.print') as mock_print:
            show_notification('Test Title', 'Test Message')
            mock_print.assert_called_once_with('Test Title: Test Message')
    
    def test_get_unique_subtitle_path_special_characters(self):
        """Test subtitle path with special characters in filename"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with spaces and special chars
            test_cases = [
                'movie with spaces.mp4',
                'show-with-dashes.mkv',
                'film_with_underscores.avi',
                'video.with.dots.mp4',
                'mixed-case.Video.Mp4'
            ]
            
            for video_name in test_cases:
                with self.subTest(video_name=video_name):
                    video_path = os.path.join(temp_dir, video_name)
                    Path(video_path).touch()
                    
                    sub_path = get_unique_subtitle_path(video_path, 'pt-br')
                    
                    # Should create valid filename
                    self.assertTrue(str(sub_path).startswith(temp_dir))
                    self.assertTrue(str(sub_path).endswith('.pt-br.srt'))
                    self.assertIn(Path(video_name).stem, str(sub_path))

if __name__ == '__main__':
    unittest.main()
