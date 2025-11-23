import os
import subprocess
import time
from pathlib import Path
from .config import Config
from .utils import is_video_file, get_unique_subtitle_path

class SubtitleDownloader:
    def __init__(self, config_file=None):
        self.config = Config(config_file)
    
    def rename_subtitle_file(self, video_path, language):
        """Renames the subtitle file to match video name"""
        video_dir = Path(video_path).parent
        current_time = time.time()
        
        for file in video_dir.iterdir():
            if file.suffix.lower() == '.srt':
                file_time = file.stat().st_mtime
                if current_time - file_time < 60:
                    new_path = get_unique_subtitle_path(video_path, language)
                    file.rename(new_path)
                    return new_path.name
        return None

    def download_subtitles(self, file_path, language):
        """Executes subtitle download for specific language"""
        cmd = [
            "python3", "-m", "subliminal", 
            "download", 
            "-l", language,
            "--provider", "opensubtitles",
            "--verbose",
            file_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            return None

    def download_for_file(self, file_path):
        """Main method to download subtitles for a file"""
        if not is_video_file(file_path):
            return False, "Invalid video file"
        
        if not os.path.exists(file_path):
            return False, "File not found"
        
        # Try Portuguese first
        result_ptbr = self.download_subtitles(file_path, "pt-br")
        
        if result_ptbr and result_ptbr.returncode == 0 and ("Downloaded" in result_ptbr.stdout or "1 subtitle downloaded" in result_ptbr.stdout):
            renamed_file = self.rename_subtitle_file(file_path, "pt-br")
            return True, f"Portuguese subtitle downloaded: {renamed_file if renamed_file else 'file.srt'}"
        else:
            # Try English
            result_en = self.download_subtitles(file_path, "en")
            
            if result_en and result_en.returncode == 0 and ("Downloaded" in result_en.stdout or "1 subtitle downloaded" in result_en.stdout):
                renamed_file = self.rename_subtitle_file(file_path, "en")
                return True, f"English subtitle downloaded: {renamed_file if renamed_file else 'file.srt'}"
            else:
                return False, "No subtitles found in any language"

    def batch_download(self, folder_path):
        """Downloads subtitles for all video files in a folder"""
        results = {}
        folder = Path(folder_path)
        
        if not folder.is_dir():
            return {"error": "Invalid folder path"}
        
        for file_path in folder.iterdir():
            if is_video_file(file_path):
                success, message = self.download_for_file(str(file_path))
                results[str(file_path)] = {"success": success, "message": message}
        
        return results # Core functionality will be implemented here
