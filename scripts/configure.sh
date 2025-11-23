#!/bin/bash
echo "🎬 Subtitle Downloader Configuration"
echo "===================================="

# Detectar se é RPM ou DEB
if command -v rpm > /dev/null 2>&1; then
    echo "📦 RPM-based system detected"
    PACKAGE_MANAGER="rpm"
elif command -v dpkg > /dev/null 2>&1; then
    echo "📦 DEB-based system detected"
    PACKAGE_MANAGER="deb"
else
    echo "⚠️  System not identified (neither RPM nor DEB)"
    PACKAGE_MANAGER="unknown"
fi

# Verificar se subliminal está instalado
if ! command -v python3 -c "import subliminal" &> /dev/null; then
    echo "❌ Subliminal not found!"
    echo "📦 Installing subliminal..."
    pip3 install --user subliminal
    
    if [ $? -ne 0 ]; then
        echo "❌ Error installing subliminal!"
        exit 1
    fi
fi

# Configuração de idiomas
echo ""
echo "🌎 Language Configuration:"
echo "   Primary: Portuguese Brazilian (pt-br)"
echo "   Secondary: English (en)"
echo ""

echo "📝 You need a free account at OpenSubtitles.org"
echo "   Visit: https://www.opensubtitles.org/pt/newuser"
echo ""

read -p "Enter your OpenSubtitles username: " username
read -s -p "Enter your OpenSubtitles password: " password
echo

echo ""
echo "🔧 Configuring..."

# Testar a configuração
echo "🧪 Testing configuration..."
if python3 -m subliminal --opensubtitles "$username" "$password" download -l pt-br --help > /dev/null 2>&1; then
    echo "✅ Configuration saved successfully!"
    echo ""
    echo "🎉 Now you can:"
    echo "   1. Right-click on video files"
    echo "   2. Select 'Download Subtitle'" 
    echo "   3. Portuguese subtitles will be downloaded first, then English"
else
    echo "❌ Configuration error. Check:"
    echo "   - Correct username and password"
    echo "   - Internet connection"
    echo "   - Account activated on OpenSubtitles"
    exit 1
fi
