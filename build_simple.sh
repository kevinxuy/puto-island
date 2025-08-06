#!/bin/bash

# Simple Android build script with minimal dependencies

echo "======================================"
echo "Puto Island Android Build - Simple"  
echo "======================================"

# Set up environment
export PATH="/opt/homebrew/bin:/opt/homebrew/Cellar/openjdk@17/17.0.16/bin:$HOME/Library/Python/3.9/bin:$PATH"
export JAVA_HOME="/opt/homebrew/Cellar/openjdk@17/17.0.16/libexec/openjdk.jdk/Contents/Home"

echo "✅ Setting up minimal build environment..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf .buildozer/android/app
rm -rf .buildozer/android/platform/build-*
rm -rf bin/

# Create a minimal buildozer spec for testing
echo "📝 Creating minimal buildozer config..."
cat > buildozer_minimal.spec << 'EOF'
[app]
title = Puto Island
package.name = putoisland
package.domain = org.puto
source.dir = .
source.include_exts = py,png,jpg,json,txt,mp4
source.include_patterns = assets/**,*.py,*.json,*.txt
version = 1.0.0
requirements = python3,pygame==2.1.3
orientation = portrait
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
EOF

# Run minimal build
echo "📱 Starting minimal Android build..."
BUILDOZER_SPEC_PATH=buildozer_minimal.spec python3 -m buildozer android debug

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "🎉 BUILD SUCCESSFUL! 🎉"
    ls -la bin/*.apk 2>/dev/null
else
    echo "❌ Build failed. Trying fallback approach..."
    
    # Fallback: Try with even simpler config
    echo "🔄 Attempting fallback build with pygame 2.0.1..."
    sed -i '' 's/pygame==2.1.3/pygame==2.0.1/' buildozer_minimal.spec
    BUILDOZER_SPEC_PATH=buildozer_minimal.spec python3 -m buildozer android debug
fi

echo ""
echo "Build completed. Check bin/ folder for APK files."