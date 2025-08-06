#!/usr/bin/env python3
"""
Manual APK building script that bypasses buildozer SDK issues
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ Success: {cmd}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def main():
    print("🎮 Manual Puto Island APK Builder")
    print("=" * 50)
    
    # Set up environment
    os.environ["PATH"] = f"{os.path.expanduser('~/Library/Python/3.9/bin')}:/opt/homebrew/bin:{os.environ['PATH']}"
    os.environ["JAVA_HOME"] = "/opt/homebrew/Cellar/openjdk@17/17.0.16/libexec/openjdk.jdk/Contents/Home"
    
    # Create ultra-minimal spec
    minimal_spec = """[app]
title = Puto Island
package.name = putoisland  
package.domain = org.puto
source.dir = .
source.include_exts = py,png,jpg
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
warn_on_root = 0"""

    print("📝 Creating minimal buildozer spec...")
    with open("buildozer.spec", "w") as f:
        f.write(minimal_spec)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    if os.path.exists("bin"):
        shutil.rmtree("bin")
    if os.path.exists(".buildozer/android/app"):
        shutil.rmtree(".buildozer/android/app")
    
    # Skip SDK manager by creating dummy platform-tools
    sdk_path = Path.home() / ".buildozer/android/platform/android-sdk"
    platform_tools = sdk_path / "platform-tools"
    platform_tools.mkdir(parents=True, exist_ok=True)
    
    # Create dummy adb if it doesn't exist
    adb_path = platform_tools / "adb"
    if not adb_path.exists():
        adb_path.write_text("#!/bin/bash\necho 'dummy adb'")
        adb_path.chmod(0o755)
    
    print("🔧 Starting APK build...")
    
    # Try the build
    success, output = run_command("python3 -m buildozer android debug")
    
    if success:
        print("\n🎉 APK BUILD SUCCESSFUL!")
        if os.path.exists("bin"):
            apk_files = list(Path("bin").glob("*.apk"))
            if apk_files:
                print(f"📱 APK created: {apk_files[0]}")
                print(f"📦 Size: {apk_files[0].stat().st_size / 1024 / 1024:.1f} MB")
            else:
                print("⚠️ Build succeeded but APK not found in bin/")
    else:
        print("\n❌ Build failed")
        print("💡 Common solutions:")
        print("- Check internet connection")
        print("- Free up disk space (need ~2GB)")
        print("- Run: brew install autoconf automake libtool")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)