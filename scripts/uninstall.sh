#!/bin/bash
# Subtitle Downloader Uninstallation Script

USER_HOME="$HOME"

echo "🗑️ Uninstalling Subtitle Downloader..."
echo "======================================"

# Function to detect package manager
detect_package_manager() {
    if command -v apt > /dev/null 2>&1; then
        echo "apt"
    elif command -v dnf > /dev/null 2>&1; then
        echo "dnf"
    elif command -v yum > /dev/null 2>&1; then
        echo "yum"
    elif command -v zypper > /dev/null 2>&1; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

# Function to remove context menus
remove_context_menus() {
    echo "🗑️ Removing context menus..."
    
    # Remove from all possible file managers
    rm -f ~/.local/share/nautilus/scripts/download-subtitle.py
    rm -f ~/.local/share/nemo/scripts/download-subtitle.py
    rm -f ~/.config/caja/scripts/download-subtitle.py
    rm -f ~/.local/share/kio/servicemenus/download-subtitle.desktop
    rm -f ~/.local/share/file-manager/actions/download-subtitle.desktop
    
    # Special handling for Thunar
    if [ -f ~/.config/Thunar/uca.xml ]; then
        sed -i '/Download Subtitle/,/<\/action>/d' ~/.config/Thunar/uca.xml
        echo "✅ Thunar context menu removed"
    fi
    
    echo "✅ Context menus removed"
}

# Function to remove links
remove_links() {
    echo "🔗 Removing symbolic links..."
    
    # Remove user bin link
    if [ -L "$USER_HOME/.local/bin/download-subtitle.py" ]; then
        rm "$USER_HOME/.local/bin/download-subtitle.py"
        echo "✅ User script removed"
    else
        echo "⚠️ User script not found"
    fi
    
    # Remove system link
    if [ -L "/usr/local/bin/download-subtitle.py" ]; then
        sudo rm -f "/usr/local/bin/download-subtitle.py"
        echo "✅ System script removed"
    else
        echo "⚠️ System script not found"
    fi
    
    # Remove source code
    if [ -d "$USER_HOME/.local/subtitle-downloader/src" ]; then
        rm -rf "$USER_HOME/.local/subtitle-downloader/src"
        echo "✅ Source code removed"
    fi
    
    remove_context_menus
}

# Function to ask about dependencies
ask_about_dependencies() {
    echo ""
    read -p "❓ Remove Python dependencies (Subliminal)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Removing Python dependencies..."
        pip3 uninstall -y subliminal
        echo "✅ Python dependencies removed"
    else
        echo "ℹ️ Python dependencies kept"
    fi
    
    echo ""
    read -p "❓ Remove system packages (PyQt5/GTK, libnotify)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PACKAGE_MANAGER=$(detect_package_manager)
        echo "📦 Removing system packages..."
        
        case $PACKAGE_MANAGER in
            "apt")
                sudo apt remove -y python3-pyqt5 python3-gi python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin
                ;;
            "dnf"|"yum")
                sudo $PACKAGE_MANAGER remove -y python3-qt5 python3-gobject gtk3 libnotify
                ;;
            "zypper")
                sudo zypper remove -y python3-qt5 python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-3_0 libnotify-tools
                ;;
        esac
        echo "✅ System packages removed"
    else
        echo "ℹ️ System packages kept"
    fi
}

# Main uninstallation function
main() {
    remove_links
    ask_about_dependencies
    
    echo ""
    echo "✅ Uninstallation completed!"
    echo "🔄 Restart your file manager(s) to see changes"
}

# Execute uninstallation
main
