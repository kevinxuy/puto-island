# Building Puto Island for Android

This guide will help you build your Pygame game as an Android APK that can run on your phone.

## Prerequisites

Buildozer works on macOS and Linux. Since you have a MacBook, this is perfect!

## Installation Steps for macOS

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install System Dependencies

```bash
# Install essential tools
brew install python3 git zip unzip autoconf libtool pkg-config

# Install Java (required for Android SDK)
brew install openjdk@11

# Add Java to PATH
echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install Cython and Buildozer

```bash
# Install using pip3
pip3 install --user cython buildozer

# Or if you prefer using brew's Python
brew install python3
pip3 install cython buildozer
```

### 4. Setup Android SDK/NDK (Automatic)

Buildozer will automatically download Android SDK/NDK when you first build. No manual setup needed!

### 5. Copy Your Game Files

Copy your entire Puto6 folder to your Mac (if it's not already there):
- All Python files (main_game.py, temple1.py, etc.)
- assets/ folder with all images
- game_manager.py
- buildozer.spec
- requirements.txt

### 6. Prepare main.py

Since Buildozer looks for main.py, create a copy:

```bash
cd /path/to/your/Puto6
cp main_game.py main.py
```

### 7. Build the APK

```bash
# Navigate to your game folder
cd /path/to/your/Puto6

# Build the APK (first time will take 30-60 minutes)
buildozer android debug
```

This will:
- Download Android SDK/NDK (first time only, ~2GB)
- Create a virtual environment
- Install dependencies
- Build the APK

The APK will be created in `bin/putoisland-1.0.0-arm64-v8a-debug.apk`

### 8. Install on Phone

**Option 1: Transfer manually**
- Copy the APK to your phone
- Enable "Install from unknown sources" in Settings
- Install the APK

**Option 2: Use ADB (if phone is connected)**
```bash
# Install Android SDK platform-tools first
brew install android-platform-tools

# Install the APK
adb install bin/putoisland-1.0.0-arm64-v8a-debug.apk
```

## macOS-Specific Notes

### Xcode Command Line Tools
If you get compilation errors, install Xcode command line tools:
```bash
xcode-select --install
```

### M1/M2 Mac Compatibility
On Apple Silicon Macs, you might need:
```bash
# If you get architecture errors
arch -x86_64 buildozer android debug
```

### Python Path Issues
If buildozer can't find Python:
```bash
# Add to ~/.zshrc
export PATH="/opt/homebrew/bin:$PATH"
export PATH="/usr/local/bin:$PATH"
```

## Important Notes

### Touch Controls
Your game currently uses mouse controls. You'll need to modify the code to handle touch:

```python
# In each game file, modify event handling:
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    # This works for both mouse and touch
```

### Screen Resolution
Android screens vary. You may want to add screen scaling:

```python
# Get device screen size and scale accordingly
info = pygame.display.Info()
scale_x = info.current_w / 600  # Your game width
scale_y = info.current_h / 1000  # Your game height
```

### File Paths
Make sure all asset paths use forward slashes and are relative:
```python
# Good
image = pygame.image.load("./assets/temple1/t1map.png")

# Avoid absolute paths
```

## Troubleshooting

### Common Issues:

1. **Build fails**: Check buildozer.spec requirements
2. **APK crashes**: Check game_data.json file permissions
3. **Images not loading**: Verify asset paths are correct
4. **Performance issues**: Consider reducing image sizes

### Debug Mode
To see logs while testing:
```bash
adb logcat | grep python
```

## Release Build

For a release version (smaller, optimized):
```bash
buildozer android release
```

You'll need to sign the APK with a keystore for distribution.

## File Structure After Build

```
Puto6/
├── main.py (copy of main_game.py)
├── buildozer.spec
├── requirements.txt
├── assets/
├── bin/
│   └── putoisland-1.0.0-arm64-v8a-debug.apk
└── .buildozer/ (build cache)
```

## Performance Tips for Mobile

1. **Optimize Images**: Use smaller PNG files
2. **Reduce FPS**: Consider 30 FPS instead of 60
3. **Touch-Friendly UI**: Make buttons larger
4. **Battery Usage**: Add pause/resume handling

The APK should be around 20-50MB depending on your assets size.