#!/usr/bin/env python3
"""
Tests for core functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the package to Python path
package_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(package_dir))

from subtitle_downloader.core import SubtitleDownloader
from subtitle_downloader.utils import is_video_file, get_unique_subtitle_path
from subtitle_downloader.config import Config

class TestCore(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'test_config.json')
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_config_creation(self):
        """Test configuration file creation"""
        config = Config(self.config_file)
        
        self.assertEqual(config.get('default_language'), 'pt-br')
        self.assertEqual(config.get('fallback_language'), 'en')
        self.assertTrue(config.get('auto_rename'))
        
        # Test setting values
        config.set('test_key', 'test_value')
        self.assertEqual(config.get('test_key'), 'test_value')
    
    def test_is_video_file(self):
        """Test video file detection"""
        # Test valid video extensions
        self.assertTrue(is_video_file('movie.mp4'))
        self.assertTrue(is_video_file('film.mkv'))
        self.assertTrue(is_video_file('video.avi'))
        self.assertTrue(is_video_file('show.MP4'))  # Case insensitive
        
        # Test invalid extensions
        self.assertFalse(is_video_file('document.pdf'))
        self.assertFalse(is_video_file('image.jpg'))
        self.assertFalse(is_video_file('script.txt'))
        self.assertFalse(is_video_file('subtitle.srt'))
    
    def test_get_unique_subtitle_path(self):
        """Test unique subtitle path generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, 'test_video.mp4')
            
            # Create the video file
            Path(video_path).touch()
            
            # Test first subtitle
            sub_path = get_unique_subtitle_path(video_path, 'pt-br')
            expected_path = Path(temp_dir) / 'test_video.pt-br.srt'
            self.assertEqual(sub_path, expected_path)
            
            # Create the first subtitle file
            Path(sub_path).touch()
            
            # Test second subtitle (should get numbered)
            sub_path2 = get_unique_subtitle_path(video_path, 'pt-br')
            expected_path2 = Path(temp_dir) / 'test_video.pt-br_1.srt'
            self.assertEqual(sub_path2, expected_path2)
    
    def test_subtitle_downloader_initialization(self):
        """Test SubtitleDownloader class initialization"""
        downloader = SubtitleDownloader(self.config_file)
        
        self.assertIsNotNone(downloader.config)
        self.assertEqual(downloader.config.get('default_language'), 'pt-br')
    
    def test_opensubtitles_credentials(self):
        """Test OpenSubtitles credentials management"""
        config = Config(self.config_file)
        
        # Test setting credentials
        config.set_opensubtitles_credentials('test_user', 'test_pass')
        
        # Test getting credentials
        username, password = config.get_opensubtitles_credentials()
        self.assertEqual(username, 'test_user')
        self.assertEqual(password, 'test_pass')

class TestBatchOperations(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'test_config.json')
        
        # Create some test video files
        self.video_files = [
            os.path.join(self.test_dir, 'test1.mp4'),
            os.path.join(self.test_dir, 'test2.mkv'),
            os.path.join(self.test_dir, 'test3.avi')
        ]
        
        for video_file in self.video_files:
            Path(video_file).touch()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_batch_download_with_invalid_folder(self):
        """Test batch download with invalid folder"""
        downloader = SubtitleDownloader(self.config_file)
        
        result = downloader.batch_download('/nonexistent/path')
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Invalid folder path')
    
    def test_batch_download_empty_folder(self):
        """Test batch download with empty folder"""
        empty_dir = tempfile.mkdtemp()
        
        try:
            downloader = SubtitleDownloader(self.config_file)
            result = downloader.batch_download(empty_dir)
            
            # Should return empty results for empty folder
            self.assertEqual(len(result), 0)
        finally:
            import shutil
            shutil.rmtree(empty_dir)

if __name__ == '__main__':
    unittest.main()
