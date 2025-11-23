import json
import os
from pathlib import Path

class Config:
    def __init__(self, config_file=None):
        if config_file is None:
            self.config_file = Path.home() / ".config" / "subtitle-downloader" / "config.json"
        else:
            self.config_file = Path(config_file)
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_config()
    
    def load_config(self):
        """Loads configuration from file"""
        default_config = {
            "default_language": "pt-br",
            "fallback_language": "en",
            "providers": ["opensubtitles"],
            "download_folder": str(Path.home() / "Subtitles"),
            "auto_rename": True,
            "opensubtitles_username": "",
            "opensubtitles_password": ""
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        self._config = default_config
        
        # Save default config if it doesn't exist
        if not self.config_file.exists():
            self.save_config()
    
    def save_config(self):
        """Saves configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Gets a configuration value"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """Sets a configuration value"""
        self._config[key] = value
        self.save_config()
    
    def set_opensubtitles_credentials(self, username, password):
        """Sets OpenSubtitles credentials"""
        self.set("opensubtitles_username", username)
        self.set("opensubtitles_password", password)
    
    def get_opensubtitles_credentials(self):
        """Gets OpenSubtitles credentials"""
        return self.get("opensubtitles_username"), self.get("opensubtitles_password")
