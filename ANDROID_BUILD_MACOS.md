# Building Puto Island for Android on macOS

## Quick Start

If you want to build right away, follow these steps:

### Step 1: Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, follow the instructions to add Homebrew to your PATH.

### Step 2: Install Java
```bash
brew install openjdk@17
```

Then add Java to your PATH:
```bash
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Build the APK
```bash
cd /Users/kevin/Documents/Puto6

# Add buildozer to PATH for this session
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Run the build (first time will take 30-60 minutes)
python3 -m buildozer android debug
```

## What Has Been Prepared

✅ **buildozer.spec** - Updated with all requirements and configurations
✅ **main.py** - Created as entry point for the app
✅ **font_helper.py** - Created to handle Chinese fonts on Android
✅ **Buildozer installed** - Via pip3
✅ **Build script** - `build_android.sh` for easy building

## Files Modified for Android

All Python files have been updated to:
- Use `python3` shebang
- Use `python3` for subprocess calls
- Use cross-platform font loading

## Known Issues to Address

### 1. OpenCV on Android
OpenCV (cv2) might not work properly on Android. The game uses it in:
- `pick.py` - For video playback
- `zjt.py` - For video handling

**Solution**: The code already has fallback handling when cv2 is not available.

### 2. Video Files
MP4 files might not play on Android without additional codecs.

**Solution**: Consider converting videos to image sequences or using Pygame's built-in animation.

### 3. File Paths
All file paths should be relative, not absolute.

**Status**: ✅ Already using relative paths in assets loading.

### 4. Touch Controls
The game currently uses mouse controls which work on Android as touch.

**Status**: ✅ `pygame.MOUSEBUTTONDOWN` works for touch input.

### 5. Screen Size
The game is designed for 600x800 portrait mode.

**Status**: ✅ buildozer.spec configured for portrait orientation.

## Building the APK

### Option 1: Use the build script
```bash
./build_android.sh
```

### Option 2: Manual build
```bash
# Ensure buildozer is in PATH
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Build debug APK
python3 -m buildozer android debug

# Or for release APK (requires signing)
python3 -m buildozer android release
```

## After Building

The APK will be in the `bin/` directory:
- Debug: `bin/putoisland-1.0.0-arm64-v8a-debug.apk`
- Release: `bin/putoisland-1.0.0-arm64-v8a-release-unsigned.apk`

## Installing on Your Phone

### Method 1: Direct Transfer
1. Transfer the APK to your phone (AirDrop, email, cloud storage)
2. On your phone: Settings → Security → Enable "Unknown sources"
3. Open the APK file on your phone and install

### Method 2: Using ADB (if USB debugging enabled)
```bash
# Install Android platform tools
brew install android-platform-tools

# Connect phone via USB with debugging enabled
adb install bin/putoisland-1.0.0-arm64-v8a-debug.apk
```

## Troubleshooting

### Build fails with Java error
```bash
# Install Java
brew install openjdk@17
# Add to PATH as shown above
```

### Build fails with "buildozer not found"
```bash
# Use Python module directly
python3 -m buildozer android debug
```

### Build fails with compilation errors
```bash
# Install Xcode command line tools
xcode-select --install
```

### APK crashes on phone
- Check `adb logcat | grep python` for errors
- Ensure all assets are included in buildozer.spec
- Verify game_save.json is handled properly

## Performance Optimization

For better performance on mobile:
1. Reduce image sizes if needed
2. Lower FPS to 30 in game files if needed
3. Disable unnecessary visual effects

## Next Steps

1. Install Homebrew and Java (if not done)
2. Run `./build_android.sh` or `python3 -m buildozer android debug`
3. Wait for build to complete (30-60 minutes first time)
4. Install APK on your phone
5. Test and enjoy!

## Support

If you encounter issues:
1. Check the buildozer log for specific errors
2. Ensure all dependencies are installed
3. Verify file permissions are correct
4. Try cleaning the build: `buildozer android clean`