#!/bin/bash

# Build script for Puto Island Android APK

echo "======================================"
echo "Puto Island Android Build Script"
echo "======================================"

# Check if buildozer is available
if ! command -v buildozer &> /dev/null && ! python3 -m buildozer --version &> /dev/null; then
    echo "❌ Buildozer not found!"
    echo "Please install it with: pip3 install --user buildozer"
    exit 1
fi

# Add Python user bin to PATH for this session
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "✅ Creating main.py..."
    cp main_game.py main.py 2>/dev/null || echo "⚠️  main.py already exists or couldn't create"
fi

echo ""
echo "📱 Starting Android build..."
echo "This will take 30-60 minutes on first run as it downloads Android SDK/NDK"
echo ""

# Try to use buildozer from PATH first, then try Python module
if command -v buildozer &> /dev/null; then
    buildozer android debug
else
    python3 -m buildozer android debug
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📦 APK location: bin/*.apk"
    echo ""
    echo "To install on your phone:"
    echo "1. Transfer the APK to your phone"
    echo "2. Enable 'Install from unknown sources' in Settings"
    echo "3. Install the APK"
else
    echo ""
    echo "❌ Build failed. Please check the errors above."
    echo ""
    echo "Common issues:"
    echo "- Missing Java: Install with Homebrew"
    echo "- Missing dependencies: Check buildozer.spec"
    echo "- Permission issues: Run with proper permissions"
fi