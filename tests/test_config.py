#!/usr/bin/env python3
"""
Tests for configuration management
"""

import unittest
import tempfile
import os
import json
import sys
from pathlib import Path

# Add the package to Python path
package_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(package_dir))

from subtitle_downloader.config import Config

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'test_config.json')
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_config_default_values(self):
        """Test default configuration values"""
        config = Config(self.config_file)
        
        expected_defaults = {
            'default_language': 'pt-br',
            'fallback_language': 'en',
            'providers': ['opensubtitles'],
            'auto_rename': True
        }
        
        for key, expected_value in expected_defaults.items():
            self.assertEqual(config.get(key), expected_value)
    
    def test_config_file_creation(self):
        """Test that config file is created automatically"""
        # Config file should not exist initially
        self.assertFalse(os.path.exists(self.config_file))
        
        # Creating Config should create the file
        config = Config(self.config_file)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Verify file content
        with open(self.config_file, 'r') as f:
            file_content = json.load(f)
        
        self.assertIn('default_language', file_content)
        self.assertIn('auto_rename', file_content)
    
    def test_config_persistence(self):
        """Test that config changes are persisted"""
        config = Config(self.config_file)
        
        # Change some values
        config.set('test_key', 'test_value')
        config.set('default_language', 'es')
        
        # Create new config instance to test persistence
        config2 = Config(self.config_file)
        
        # Values should be persisted
        self.assertEqual(config2.get('test_key'), 'test_value')
        self.assertEqual(config2.get('default_language'), 'es')
    
    def test_config_get_with_default(self):
        """Test get method with default values"""
        config = Config(self.config_file)
        
        # Test existing key
        self.assertEqual(config.get('default_language'), 'pt-br')
        
        # Test non-existing key with default
        self.assertEqual(config.get('non_existing_key'), None)
        self.assertEqual(config.get('non_existing_key', 'default_value'), 'default_value')
    
    def test_opensubtitles_credentials_storage(self):
        """Test OpenSubtitles credentials storage and retrieval"""
        config = Config(self.config_file)
        
        # Set credentials
        config.set_opensubtitles_credentials('my_username', 'my_password')
        
        # Retrieve credentials
        username, password = config.get_opensubtitles_credentials()
        
        self.assertEqual(username, 'my_username')
        self.assertEqual(password, 'my_password')
        
        # Verify persistence
        config2 = Config(self.config_file)
        username2, password2 = config2.get_opensubtitles_credentials()
        
        self.assertEqual(username2, 'my_username')
        self.assertEqual(password2, 'my_password')
    
    def test_config_with_invalid_json(self):
        """Test config handling with invalid JSON file"""
        # Create invalid JSON file
        with open(self.config_file, 'w') as f:
            f.write('invalid json content')
        
        # Should not crash and should use defaults
        config = Config(self.config_file)
        self.assertEqual(config.get('default_language'), 'pt-br')
    
    def test_config_directory_creation(self):
        """Test that config directory is created if needed"""
        nested_config_file = os.path.join(
            self.test_dir, 'nested', 'config', 'test_config.json'
        )
        
        # Directory should not exist
        self.assertFalse(os.path.exists(os.path.dirname(nested_config_file)))
        
        # Creating config should create directory
        config = Config(nested_config_file)
        self.assertTrue(os.path.exists(os.path.dirname(nested_config_file)))
    
    def test_multiple_config_instances(self):
        """Test multiple config instances don't interfere"""
        config1 = Config(self.config_file)
        config2 = Config(self.config_file)
        
        # Set value in first instance
        config1.set('shared_key', 'value1')
        
        # Should be visible in second instance
        self.assertEqual(config2.get('shared_key'), 'value1')
        
        # Change in second instance
        config2.set('shared_key', 'value2')
        
        # Should be visible in first instance
        self.assertEqual(config1.get('shared_key'), 'value2')

class TestConfigEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_config_with_empty_file(self):
        """Test config with empty file"""
        config_file = os.path.join(self.test_dir, 'empty_config.json')
        
        # Create empty file
        Path(config_file).touch()
        
        # Should use defaults
        config = Config(config_file)
        self.assertEqual(config.get('default_language'), 'pt-br')
    
    def test_config_with_read_only_file(self):
        """Test config with read-only file (should not crash)"""
        config_file = os.path.join(self.test_dir, 'readonly_config.json')
        
        config = Config(config_file)
        config.set('test_key', 'test_value')
        
        # Make file read-only
        os.chmod(config_file, 0o444)
        
        try:
            # Should handle write error gracefully
            config.set('another_key', 'another_value')
        except Exception as e:
            self.fail(f"Config should handle read-only files gracefully: {e}")
        finally:
            # Restore permissions for cleanup
            os.chmod(config_file, 0o644)
    
    def test_unicode_in_config(self):
        """Test config with unicode characters"""
        config_file = os.path.join(self.test_dir, 'unicode_config.json')
        
        config = Config(config_file)
        
        # Test unicode values
        unicode_value = 'Português Brasileiro 🇧🇷'
        config.set('unicode_key', unicode_value)
        
        # Verify persistence
        config2 = Config(config_file)
        self.assertEqual(config2.get('unicode_key'), unicode_value)

if __name__ == '__main__':
    unittest.main()
