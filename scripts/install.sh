#!/bin/bash
# Subtitle Downloader Installation Script

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_HOME="$HOME"

echo "🚀 Installing Subtitle Downloader..."
echo "======================================"

# Function to detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_LIKE=$ID_LIKE
    else
        echo "❌ Could not detect distribution"
        exit 1
    fi
    
    echo "📋 Detected distribution: $DISTRO"
    
    # Detect package manager
    if command -v apt > /dev/null 2>&1; then
        PACKAGE_MANAGER="apt"
        PACKAGE_SUFFIX="deb"
    elif command -v dnf > /dev/null 2>&1; then
        PACKAGE_MANAGER="dnf"
        PACKAGE_SUFFIX="rpm"
    elif command -v yum > /dev/null 2>&1; then
        PACKAGE_MANAGER="yum"
        PACKAGE_SUFFIX="rpm"
    elif command -v zypper > /dev/null 2>&1; then
        PACKAGE_MANAGER="zypper"
        PACKAGE_SUFFIX="rpm"
    else
        echo "❌ Unsupported package manager"
        exit 1
    fi
    
    echo "📦 Package manager: $PACKAGE_MANAGER ($PACKAGE_SUFFIX)"
}

# Function to install packages based on distribution
install_package() {
    local package=$1
    echo "📦 Installing $package..."
    
    case $PACKAGE_MANAGER in
        "apt")
            sudo apt update && sudo apt install -y "$package"
            ;;
        "dnf")
            sudo dnf install -y "$package"
            ;;
        "yum")
            sudo yum install -y "$package"
            ;;
        "zypper")
            sudo zypper install -y "$package"
            ;;
        *)
            echo "❌ Unsupported package manager: $PACKAGE_MANAGER"
            exit 1
            ;;
    esac
}

# Function to detect file managers
detect_file_managers() {
    echo "🔍 Detecting file managers..."
    FILE_MANAGERS=()
    
    # Check for popular file managers
    if command -v nautilus &> /dev/null; then
        FILE_MANAGERS+=("nautilus")
        echo "✅ Nautilus (GNOME) detected"
    fi
    
    if command -v nemo &> /dev/null; then
        FILE_MANAGERS+=("nemo")
        echo "✅ Nemo (Cinnamon) detected"
    fi
    
    if command -v caja &> /dev/null; then
        FILE_MANAGERS+=("caja")
        echo "✅ Caja (MATE) detected"
    fi
    
    if command -v thunar &> /dev/null; then
        FILE_MANAGERS+=("thunar")
        echo "✅ Thunar (XFCE) detected"
    fi
    
    if command -v dolphin &> /dev/null; then
        FILE_MANAGERS+=("dolphin")
        echo "✅ Dolphin (KDE) detected"
    fi
    
    if command -v pcmanfm &> /dev/null; then
        FILE_MANAGERS+=("pcmanfm")
        echo "✅ PCManFM (LXDE) detected"
    fi
    
    if command -v pcmanfm-qt &> /dev/null; then
        FILE_MANAGERS+=("pcmanfm-qt")
        echo "✅ PCManFM-Qt (LXQt) detected"
    fi
    
    if [ ${#FILE_MANAGERS[@]} -eq 0 ]; then
        echo "⚠️ No supported file managers detected"
    else
        echo "📋 Found ${#FILE_MANAGERS[@]} file manager(s)"
    fi
}

# Function to ask which file managers to configure
ask_file_manager_config() {
    echo ""
    echo "🎯 File Manager Configuration"
    echo "============================"
    
    if [ ${#FILE_MANAGERS[@]} -eq 0 ]; then
        echo "❌ No supported file managers detected automatically."
        echo "You can manually install context menu for specific file managers later."
        return
    fi
    
    echo "Detected file managers:"
    for i in "${!FILE_MANAGERS[@]}"; do
        echo "  $((i+1)). ${FILE_MANAGERS[$i]}"
    done
    
    echo ""
    echo "Select file managers to install context menu:"
    
    SELECTED_MANAGERS=()
    for manager in "${FILE_MANAGERS[@]}"; do
        read -p "Install for $manager? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            SELECTED_MANAGERS+=("$manager")
        fi
    done
    
    if [ ${#SELECTED_MANAGERS[@]} -eq 0 ]; then
        echo "ℹ️ No file managers selected for context menu installation."
    else
        echo "✅ Will install context menu for: ${SELECTED_MANAGERS[*]}"
    fi
}

# Function to install context menus
install_context_menus() {
    if [ ${#SELECTED_MANAGERS[@]} -eq 0 ]; then
        return
    fi
    
    echo ""
    echo "📁 Installing context menus..."
    
    for manager in "${SELECTED_MANAGERS[@]}"; do
        case $manager in
            "nautilus")
                echo "🔧 Installing for Nautilus..."
                mkdir -p ~/.local/share/nautilus/scripts/
                cp "$PROJECT_DIR/share/file-manager/scripts/download-subtitle.py" ~/.local/share/nautilus/scripts/
                chmod +x ~/.local/share/nautilus/scripts/download-subtitle.py
                ;;
            "nemo")
                echo "🔧 Installing for Nemo..."
                mkdir -p ~/.local/share/nemo/scripts/
                cp "$PROJECT_DIR/share/file-manager/scripts/download-subtitle.py" ~/.local/share/nemo/scripts/
                chmod +x ~/.local/share/nemo/scripts/download-subtitle.py
                ;;
            "caja")
                echo "🔧 Installing for Caja..."
                mkdir -p ~/.config/caja/scripts/
                cp "$PROJECT_DIR/share/file-manager/scripts/download-subtitle.py" ~/.config/caja/scripts/
                chmod +x ~/.config/caja/scripts/download-subtitle.py
                ;;
            "thunar")
                echo "🔧 Installing for Thunar..."
                mkdir -p ~/.config/Thunar/
                # Thunar requires special UCA configuration
                install_thunar_context
                ;;
            "dolphin")
                echo "🔧 Installing for Dolphin..."
                mkdir -p ~/.local/share/kio/servicemenus/
                cp "$PROJECT_DIR/share/file-manager/servicemenus/download-subtitle.desktop" ~/.local/share/kio/servicemenus/
                ;;
            "pcmanfm"|"pcmanfm-qt")
                echo "🔧 Installing for PCManFM..."
                mkdir -p ~/.local/share/file-manager/actions/
                cp "$PROJECT_DIR/share/file-manager/actions/download-subtitle.desktop" ~/.local/share/file-manager/actions/
                update-desktop-database ~/.local/share/file-manager/actions/
                ;;
        esac
        echo "✅ Context menu installed for $manager"
    done
}

# Special function for Thunar UCA configuration
install_thunar_context() {
    THUNAR_UCA_FILE="$HOME/.config/Thunar/uca.xml"
    
    # Create or update Thunar UCA configuration
    if [ ! -f "$THUNAR_UCA_FILE" ]; then
        cat > "$THUNAR_UCA_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
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
</actions>
EOF
    else
        # Check if action already exists
        if ! grep -q "Download Subtitle" "$THUNAR_UCA_FILE"; then
            # Insert action before closing </actions> tag
            sed -i '/<\/actions>/i\
<action>\
    <icon>text-x-subtitle</icon>\
    <name>Download Subtitle</name>\
    <unique-id>1670954249879849-1</unique-id>\
    <command>download-subtitle.py %f</command>\
    <description>Download subtitle for video file</description>\
    <patterns>*</patterns>\
    <video-files/>\
</action>' "$THUNAR_UCA_FILE"
        fi
    fi
    echo "✅ Thunar context menu configured"
}

# Function to check and install dependencies
check_and_install_dependencies() {
    echo "🔍 Checking dependencies..."
    
    # Detect distribution first
    detect_distro
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 not found!"
        echo "📦 Installing Python3..."
        install_package "python3"
    else
        echo "✅ Python3 found: $(python3 --version)"
    fi
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 not found!"
        echo "📦 Installing pip3..."
        case $PACKAGE_MANAGER in
            "apt") install_package "python3-pip" ;;
            "dnf"|"yum") install_package "python3-pip" ;;
            "zypper") install_package "python3-pip" ;;
        esac
    else
        echo "✅ pip3 found: $(pip3 --version)"
    fi
    
    # Check if subliminal is installed
    if ! python3 -c "import subliminal" &> /dev/null; then
        echo "❌ Subliminal not found!"
        echo "📦 Installing subliminal..."
        pip3 install --user subliminal
    else
        echo "✅ Subliminal found"
    fi
    
    # Detect which GUI to install
    echo "🎨 Detecting graphical environment..."
    if command -v pcmanfm-qt &> /dev/null || [[ "$XDG_CURRENT_DESKTOP" == *"Qt"* ]] || [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]]; then
        echo "✅ Qt environment detected"
        GUI_PREFERENCE="qt"
    else
        echo "✅ GTK environment detected"
        GUI_PREFERENCE="gtk"
    fi
    
    # Install dependencies based on preference
    if [ "$GUI_PREFERENCE" = "qt" ]; then
        echo "📦 Installing Qt dependencies..."
        if ! python3 -c "import PyQt5" &> /dev/null; then
            case $PACKAGE_MANAGER in
                "apt") install_package "python3-pyqt5" ;;
                "dnf"|"yum") install_package "python3-qt5" ;;
                "zypper") install_package "python3-qt5" ;;
            esac
        else
            echo "✅ PyQt5 found"
        fi
    else
        echo "📦 Installing GTK dependencies..."
        if ! python3 -c "import gi; gi.require_version('Gtk', '3.0')" &> /dev/null; then
            case $PACKAGE_MANAGER in
                "apt") install_package "python3-gi python3-gi-cairo gir1.2-gtk-3.0" ;;
                "dnf"|"yum") install_package "python3-gobject gtk3" ;;
                "zypper") install_package "python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-3_0" ;;
            esac
        else
            echo "✅ Python GTK3 found"
        fi
    fi
    
    # Check if notify-send is available
    if ! command -v notify-send &> /dev/null; then
        echo "❌ notify-send not found!"
        echo "📦 Installing libnotify..."
        case $PACKAGE_MANAGER in
            "apt") install_package "libnotify-bin" ;;
            "dnf"|"yum") install_package "libnotify" ;;
            "zypper") install_package "libnotify-tools" ;;
        esac
    else
        echo "✅ notify-send found"
    fi
    
    echo "✅ All dependencies checked!"
}

# Function to configure OpenSubtitles
configure_opensubtitles() {
    echo ""
    read -p "🎯 Configure OpenSubtitles now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 Running OpenSubtitles configuration..."
        "$PROJECT_DIR/scripts/configure.sh"
    else
        echo ""
        echo "📝 Remember to configure later with:"
        echo "   ~/.local/subtitle-downloader/scripts/configure.sh"
    fi
}

# Function to install main application
install_subtitle_downloader() {
    # Check and install dependencies
    check_and_install_dependencies
    
    # Detect file managers
    detect_file_managers
    
    echo ""
    echo "📁 Creating directories..."
    mkdir -p "$USER_HOME/.local/bin"
    mkdir -p "$USER_HOME/.local/subtitle-downloader/src"
    mkdir -p "$USER_HOME/.local/subtitle-downloader/logs"
    mkdir -p "$PROJECT_DIR/share/file-manager/scripts"
    mkdir -p "$PROJECT_DIR/share/file-manager/servicemenus"
    mkdir -p "$PROJECT_DIR/share/file-manager/actions"
    
    # Copy source code to user directory
    echo "📦 Copying source code..."
    cp -r "$PROJECT_DIR/src" "$USER_HOME/.local/subtitle-downloader/"
    
    # Create symbolic links
    echo "🔗 Creating symbolic links..."
    
    # Main script
    if [ -L "$USER_HOME/.local/bin/download-subtitle.py" ]; then
        echo "🔄 Updating existing link..."
        rm "$USER_HOME/.local/bin/download-subtitle.py"
    fi
    ln -sf "$PROJECT_DIR/bin/download-subtitle.py" "$USER_HOME/.local/bin/download-subtitle.py"
    
    # Create links in /usr/local/bin for better compatibility
    echo "🔗 Creating system-wide link..."
    sudo ln -sf "$USER_HOME/.local/bin/download-subtitle.py" "/usr/local/bin/download-subtitle.py" 2>/dev/null || true
    
    # Make executable
    chmod +x "$PROJECT_DIR/bin/download-subtitle.py"
    chmod +x "$PROJECT_DIR/scripts/configure.sh"
    chmod +x "$PROJECT_DIR/scripts/uninstall.sh"
    chmod +x "$USER_HOME/.local/bin/download-subtitle.py"
    
    # Create file manager scripts
    create_file_manager_scripts
    
    echo "✅ Installation completed!"
}

# Function to create file manager scripts
create_file_manager_scripts() {
    echo "📝 Creating file manager scripts..."
    
    # Script for Nautilus, Nemo, Caja
    cat > "$PROJECT_DIR/share/file-manager/scripts/download-subtitle.py" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.expanduser("~/.local/subtitle-downloader/src"))
from subtitle_downloader.__main__ import main
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("No file selected")
        sys.exit(1)
EOF
    chmod +x "$PROJECT_DIR/share/file-manager/scripts/download-subtitle.py"
    
    # Desktop file for PCManFM
    cat > "$PROJECT_DIR/share/file-manager/actions/download-subtitle.desktop" << 'EOF'
[Desktop Entry]
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
EOF

    # Service menu for Dolphin
    cat > "$PROJECT_DIR/share/file-manager/servicemenus/download-subtitle.desktop" << 'EOF'
[Desktop Entry]
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
EOF

    echo "✅ File manager scripts created"
}

# Function to show post-installation summary
show_post_install_summary() {
    echo ""
    echo "🎉 Installation Completed!"
    echo "========================"
    echo ""
    echo "📋 What was installed:"
    echo "   ✅ Python3 and pip3"
    echo "   ✅ Subliminal"
    if [ "$GUI_PREFERENCE" = "qt" ]; then
        echo "   ✅ PyQt5 (graphical interface)"
    else
        echo "   ✅ Python GTK3 (graphical interface)"
    fi
    echo "   ✅ Libnotify (notifications)"
    echo "   ✅ Main script in: ~/.local/bin/download-subtitle.py"
    echo "   ✅ System link in: /usr/local/bin/download-subtitle.py"
    echo "   ✅ Source code in: ~/.local/subtitle-downloader/src/"
    
    if [ ${#SELECTED_MANAGERS[@]} -gt 0 ]; then
        echo "   ✅ Context menu for: ${SELECTED_MANAGERS[*]}"
    fi
    
    echo ""
    echo "🎬 Next steps:"
    if [ ${#SELECTED_MANAGERS[@]} -gt 0 ]; then
        echo "   1. Restart your file manager(s)"
    fi
    echo "   2. Configure OpenSubtitles (if not done)"
    echo "   3. Right-click on video files → 'Download Subtitle'"
    echo ""
    echo "🔧 Useful commands:"
    echo "   Configure: ~/.local/subtitle-downloader/scripts/configure.sh"
    echo "   Uninstall: ~/.local/subtitle-downloader/scripts/uninstall.sh"
    echo "   View logs: ~/.local/subtitle-downloader/logs/"
}

# Main installation function
main() {
    echo "Welcome to Subtitle Downloader Installer!"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    install_subtitle_downloader
    ask_file_manager_config
    install_context_menus
    configure_opensubtitles
    show_post_install_summary
    
    # Final configuration
    echo ""
    echo "🔄 Final configuration..."
    if [ ${#SELECTED_MANAGERS[@]} -gt 0 ]; then
        echo "🎯 Restart your file manager(s) to see the context menu"
    fi
}

# Execute main function
main
