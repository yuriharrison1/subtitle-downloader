import os
import subprocess
from pathlib import Path

def detect_file_managers():
    """Detects available file managers"""
    file_managers = []
    
    managers = {
        "nautilus": "Nautilus (GNOME)",
        "nemo": "Nemo (Cinnamon)",
        "caja": "Caja (MATE)", 
        "thunar": "Thunar (XFCE)",
        "dolphin": "Dolphin (KDE)",
        "pcmanfm": "PCManFM (LXDE)",
        "pcmanfm-qt": "PCManFM-Qt (LXQt)"
    }
    
    for manager, description in managers.items():
        if subprocess.run(["which", manager], capture_output=True).returncode == 0:
            file_managers.append(manager)
    
    return file_managers

def setup_file_manager_integration(selected_managers, project_dir):
    """Sets up context menu for selected file managers"""
    for manager in selected_managers:
        try:
            if manager == "nautilus":
                setup_nautilus(project_dir)
            elif manager == "nemo":
                setup_nemo(project_dir)
            elif manager == "caja":
                setup_caja(project_dir)
            elif manager == "thunar":
                setup_thunar(project_dir)
            elif manager == "dolphin":
                setup_dolphin(project_dir)
            elif manager in ["pcmanfm", "pcmanfm-qt"]:
                setup_pcmanfm(project_dir)
        except Exception as e:
            print(f"Warning: Failed to setup {manager}: {e}")

def setup_nautilus(project_dir):
    """Sets up Nautilus integration"""
    scripts_dir = Path.home() / ".local" / "share" / "nautilus" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    script_file = scripts_dir / "download-subtitle.py"
    with open(script_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.expanduser("~/.local/subtitle-downloader/src"))
from subtitle_downloader.__main__ import main
main()
""")
    script_file.chmod(0o755)

def setup_nemo(project_dir):
    """Sets up Nemo integration"""
    scripts_dir = Path.home() / ".local" / "share" / "nemo" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    script_file = scripts_dir / "download-subtitle.py"
    with open(script_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.expanduser("~/.local/subtitle-downloader/src"))
from subtitle_downloader.__main__ import main
main()
""")
    script_file.chmod(0o755)

def setup_caja(project_dir):
    """Sets up Caja integration"""
    scripts_dir = Path.home() / ".config" / "caja" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    script_file = scripts_dir / "download-subtitle.py"
    with open(script_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.expanduser("~/.local/subtitle-downloader/src"))
from subtitle_downloader.__main__ import main
main()
""")
    script_file.chmod(0o755)

def setup_thunar(project_dir):
    """Sets up Thunar integration"""
    thunar_uca_file = Path.home() / ".config" / "Thunar" / "uca.xml"
    thunar_uca_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not thunar_uca_file.exists():
        thunar_uca_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<actions>
<action>
    <icon>text-x-subtitle</icon>
    <name>Download Subtitle</name>
    <unique-id>1670954249879849-1</unique-id>
    <command>download-subtitle.py %f</command>
    <description>Download subtitle for video file</description>
    <patterns>*</patterns>
    <video-files/>
</action>
</actions>""")
    else:
        content = thunar_uca_file.read_text()
        if "Download Subtitle" not in content:
            # Insert before closing </actions> tag
            new_content = content.replace(
                '</actions>',
                '''<action>
    <icon>text-x-subtitle</icon>
    <name>Download Subtitle</name>
    <unique-id>1670954249879849-1</unique-id>
    <command>download-subtitle.py %f</command>
    <description>Download subtitle for video file</description>
    <patterns>*</patterns>
    <video-files/>
</action>
</actions>'''
            )
            thunar_uca_file.write_text(new_content)

def setup_dolphin(project_dir):
    """Sets up Dolphin integration"""
    servicemenus_dir = Path.home() / ".local" / "share" / "kio" / "servicemenus"
    servicemenus_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = servicemenus_dir / "download-subtitle.desktop"
    desktop_file.write_text("""[Desktop Entry]
Type=Service
ServiceTypes=KonqPopupMenu/Plugin,video/*
MimeType=video/x-msvideo;video/quicktime;video/mp4;video/x-matroska;video/x-ms-wmv;video/webm;video/x-flv;video/3gpp;video/x-m4v;video/mpeg;video/x-ms-asf;video/x-ogm;video/ogg;video/dv;
Actions=download-subtitle;

[Desktop Action download-subtitle]
Name=Download Subtitle
Name[pt]=Baixar Legenda
Name[en]=Download Subtitle
Icon=text-x-subtitle
Exec=download-subtitle.py %f
""")

def setup_pcmanfm(project_dir):
    """Sets up PCManFM integration"""
    actions_dir = Path.home() / ".local" / "share" / "file-manager" / "actions"
    actions_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = actions_dir / "download-subtitle.desktop"
    desktop_file.write_text("""[Desktop Entry]
Type=Action
Name=Download Subtitle
Name[pt]=Baixar Legenda
Name[en]=Download Subtitle
Icon=text-x-subtitle
Profiles=profile-zero;

[X-Action-Profile profile-zero]
MimeTypes=video/x-msvideo;video/quicktime;video/mp4;video/x-matroska;video/x-ms-wmv;video/webm;video/x-flv;video/3gpp;video/x-m4v;video/mpeg;video/x-ms-asf;video/x-ogm;video/ogg;video/dv;video/x-matroska-3d;video/x-msvideo;video/x-theora;video/x-theora+ogg;video/x-wmv;video/x-ms-wvx;video/x-avi;
Exec=download-subtitle.py %F
SelectionCount=1
