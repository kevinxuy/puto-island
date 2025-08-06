#!/bin/bash

# Fixed Android build script for Puto Island

echo "🎮 Building Puto Island APK..."

export PATH="$HOME/Library/Python/3.9/bin:/opt/homebrew/bin:/opt/homebrew/Cellar/openjdk@17/17.0.16/bin:$PATH"
export JAVA_HOME="/opt/homebrew/Cellar/openjdk@17/17.0.16/libexec/openjdk.jdk/Contents/Home"

# Create minimal buildozer spec
cat > buildozer_minimal.spec << 'EOF'
[app]
title = Puto Island
package.name = putoisland
package.domain = org.puto
source.dir = .
source.include_exts = py,png,jpg,json,txt
version = 1.0.0
requirements = python3,pygame==2.0.1
orientation = portrait
fullscreen = 1

android.api = 28
android.minapi = 21
android.archs = armeabi-v7a
android.private_storage = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 1
warn_on_root = 0
EOF

# Copy spec over main one
cp buildozer_minimal.spec buildozer.spec

echo "🔧 Starting APK build (this may take 15-30 minutes)..."

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "✅ Creating main.py..."
    cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Main entry point for Puto Island Game
This file is required by Buildozer for Android builds
"""

# Import and run the main game
if __name__ == "__main__":
    from main_game import Game
    game = Game()
    game.run()
EOF
fi

echo ""
echo "📱 Starting Android build..."
echo "⏰ This will take 30-60 minutes on first run"
echo "📦 Downloading Android SDK/NDK (~600MB)"
echo ""

# Run buildozer
python3 -m buildozer android debug

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 Build successful!"
    echo "📦 APK location:"
    ls -la bin/*.apk 2>/dev/null || echo "   APK files not found in bin/"
    echo ""
    echo "📲 To install on your phone:"
    echo "1. Enable 'Developer options' on your phone"
    echo "2. Enable 'USB debugging' and 'Install via USB'"
    echo "3. Transfer the APK to your phone or use:"
    echo "   adb install bin/putoisland-1.0.0-*-debug.apk"
else
    echo ""
    echo "⚠️  Build process interrupted or failed (exit code: $BUILD_EXIT_CODE)"
    echo ""
    echo "If the build was downloading files and got interrupted:"
    echo "- This is normal - just run the script again"
    echo "- Downloads will resume from where they left off"
    echo ""
    echo "If there were actual errors, check above for:"
    echo "- Missing dependencies (install with brew)"
    echo "- Java path issues"
    echo "- Buildozer configuration errors"
    echo ""
    echo "To retry: ./build_android_fixed.sh"
fi

echo ""
echo "Build logs are saved in .buildozer/android/platform/python-for-android/dist/"