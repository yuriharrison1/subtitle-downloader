#!/usr/bin/env python3
"""
Thin wrapper for the subtitle downloader package
Command-line interface for subtitle downloading
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def main():
    # Add the package to Python path
    package_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    sys.path.insert(0, os.path.abspath(package_dir))
    
    try:
        from subtitle_downloader.__main__ import main as package_main
    except ImportError as e:
        print(f"❌ Error: Could not import subtitle downloader package")
        print(f"   Make sure the package is properly installed: {e}")
        sys.exit(1)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Download subtitles for video files',
        prog='download-subtitle'
    )
    
    parser.add_argument(
        'file', 
        nargs='?',
        help='Video file to download subtitles for'
    )
    
    parser.add_argument(
        '-l', '--language',
        default='pt-br',
        help='Preferred language (default: pt-br)'
    )
    
    parser.add_argument(
        '-f', '--fallback',
        default='en', 
        help='Fallback language (default: en)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process all video files in a directory'
    )
    
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List available languages and exit'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information and exit'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Force GUI mode (if available)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true', 
        help='Force command-line mode'
    )
    
    args = parser.parse_args()
    
    # Handle version flag
    if args.version:
        try:
            from subtitle_downloader import __version__
            print(f"Subtitle Downloader v{__version__}")
            sys.exit(0)
        except ImportError:
            print("Subtitle Downloader v1.0.0")
            sys.exit(0)
    
    # Handle list languages flag
    if args.list_languages:
        print("Available languages:")
        print("  pt-br  - Portuguese Brazilian")
        print("  pt     - Portuguese")
        print("  en     - English")
        print("  es     - Spanish")
        print("  fr     - French")
        print("  it     - Italian")
        print("  de     - German")
        print("  ru     - Russian")
        print("  zh     - Chinese")
        print("  ja     - Japanese")
        print("  ko     - Korean")
        sys.exit(0)
    
    # Handle batch mode
    if args.batch:
        if not args.file:
            print("❌ Error: Please specify a directory for batch processing")
            sys.exit(1)
        
        directory = Path(args.file)
        if not directory.is_dir():
            print(f"❌ Error: {args.file} is not a directory")
            sys.exit(1)
        
        print(f"🔍 Processing directory: {directory}")
        video_files = []
        
        # Supported video extensions
        video_extensions = {
            '.avi', '.mkv', '.mp4', '.mov', '.wmv', '.webm', '.flv', '.3gp', 
            '.m4v', '.mpg', '.mpeg', '.vob', '.ogv', '.ts', '.m2ts', '.divx',
            '.m4v', '.mpg', '.mpe', '.mpv', '.qt', '.asf', '.ogm', '.dv'
        }
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                video_files.append(file_path)
        
        if not video_files:
            print("❌ No video files found in the directory")
            sys.exit(1)
        
        print(f"📹 Found {len(video_files)} video files")
        
        success_count = 0
        for video_file in video_files:
            print(f"\n🎬 Processing: {video_file.name}")
            try:
                # Call the package main function for each file
                old_argv = sys.argv
                sys.argv = ['download-subtitle', str(video_file)]
                
                try:
                    package_main()
                    success_count += 1
                except SystemExit as e:
                    if e.code == 0:
                        success_count += 1
                
                sys.argv = old_argv
                
            except Exception as e:
                print(f"❌ Error processing {video_file.name}: {e}")
        
        print(f"\n✅ Batch processing completed: {success_count}/{len(video_files)} successful")
        sys.exit(0)
    
    # Handle single file mode with CLI flag
    if args.cli and args.file:
        file_path = Path(args.file)
        
        if not file_path.exists():
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)
        
        if not file_path.is_file():
            print(f"❌ Error: Not a file: {args.file}")
            sys.exit(1)
        
        # Check if it's a video file
        video_extensions = {
            '.avi', '.mkv', '.mp4', '.mov', '.wmv', '.webm', '.flv', '.3gp', 
            '.m4v', '.mpg', '.mpeg', '.vob', '.ogv', '.ts', '.m2ts', '.divx',
            '.m4v', '.mpg', '.mpe', '.mpv', '.qt', '.asf', '.ogm', '.dv'
        }
        
        if file_path.suffix.lower() not in video_extensions:
            print(f"❌ Error: Not a supported video file: {args.file}")
            print(f"   Supported formats: {', '.join(sorted(video_extensions))}")
            sys.exit(1)
        
        print(f"🎬 Downloading subtitles for: {file_path.name}")
        print(f"🌍 Language: {args.language} (fallback: {args.fallback})")
        print("⏳ Searching...")
        
        try:
            # Use subliminal directly for CLI mode
            cmd = [
                'python3', '-m', 'subliminal',
                'download',
                '-l', args.language,
                '-l', args.fallback,
                '--provider', 'opensubtitles',
                '--verbose',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if "Downloaded" in result.stdout or "1 subtitle downloaded" in result.stdout:
                    print("✅ Subtitle downloaded successfully!")
                    
                    # Try to rename the subtitle file
                    subtitle_renamed = rename_subtitle_file(file_path, args.language)
                    if subtitle_renamed:
                        print(f"📝 Subtitle renamed to: {subtitle_renamed}")
                    
                else:
                    print("❌ No subtitles found for this file")
            else:
                print("❌ Error downloading subtitle")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        sys.exit(0)
    
    # Default behavior: pass to package main
    if not args.file and len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Call the package main function
    try:
        package_main()
    except SystemExit:
        # This is expected - main() calls sys.exit()
        pass
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def rename_subtitle_file(video_path, language):
    """Renames the most recent subtitle file to match video name"""
    video_dir = Path(video_path).parent
    video_stem = Path(video_path).stem
    
    import time
    current_time = time.time()
    
    # Find the most recently created .srt file
    srt_files = []
    for file in video_dir.iterdir():
        if file.suffix.lower() == '.srt':
            file_time = file.stat().st_mtime
            # Check if file was created in the last 2 minutes
            if current_time - file_time < 120:
                srt_files.append((file, file_time))
    
    if not srt_files:
        return None
    
    # Get the most recent file
    latest_file, _ = max(srt_files, key=lambda x: x[1])
    
    # Generate new name
    base_name = f"{video_stem}.{language}.srt"
    base_path = video_dir / base_name
    
    if not base_path.exists():
        latest_file.rename(base_path)
        return base_path.name
    
    # If base name exists, add counter
    counter = 1
    while True:
        new_name = f"{video_stem}.{language}_{counter}.srt"
        new_path = video_dir / new_name
        if not new_path.exists():
            latest_file.rename(new_path)
            return new_path.name
        counter += 1

if __name__ == "__main__":
    main()
