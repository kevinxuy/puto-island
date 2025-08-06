#!/bin/bash

# Final Android build script with all dependencies

echo "======================================"
echo "Puto Island Android Build - Final"
echo "======================================"

# Set up all necessary paths
export PATH="/opt/homebrew/bin:/opt/homebrew/Cellar/openjdk@17/17.0.16/bin:$HOME/Library/Python/3.9/bin:$PATH"
export JAVA_HOME="/opt/homebrew/Cellar/openjdk@17/17.0.16/libexec/openjdk.jdk/Contents/Home"

echo "✅ Setting up environment..."
echo "   Java: $JAVA_HOME"
echo "   PATH includes Homebrew and Python"

# Verify Java is working
if java -version 2>&1 | grep -q "openjdk"; then
    echo "✅ Java is working"
else
    echo "❌ Java setup failed"
    exit 1
fi

# Verify build tools
echo "✅ Checking build tools..."
for tool in brew autoconf automake libtool pkg-config cmake; do
    if command -v $tool >/dev/null 2>&1; then
        echo "   ✓ $tool found"
    else
        echo "   ❌ $tool missing"
        exit 1
    fi
done

echo ""
echo "📱 Starting Android build with automatic dependency installation..."

# Set environment variable to automatically install missing dependencies
export BUILDOZER_AUTO_INSTALL="1"

# Create main.py if needed
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

# Run buildozer with automatic yes to all prompts
echo "y" | python3 -m buildozer android debug

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 BUILD SUCCESSFUL! 🎉"
    echo ""
    echo "📦 Your APK is ready:"
    ls -la bin/*.apk 2>/dev/null
    echo ""
    echo "📲 To install on your Android phone:"
    echo "1. Transfer the APK to your phone"
    echo "2. Enable 'Install from unknown sources' in Settings"
    echo "3. Tap the APK file to install"
    echo ""
    echo "🎮 Your game is ready for mobile!"
else
    echo ""
    echo "❌ Build failed with exit code: $BUILD_EXIT_CODE"
    echo ""
    echo "Check the output above for specific errors."
    echo "Common issues:"
    echo "- Network connectivity during downloads"
    echo "- Disk space (build requires ~2GB free)"
    echo "- Permission issues"
fi