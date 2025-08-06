[app]

# (str) Title of your application
title = Puto Island

# (str) Package name
package.name = putoisland

# (str) Package domain (needed for android/ios packaging)
package.domain = org.puto

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt,ttf,ttc,mp4

# (list) List of inclusions using pattern matching
source.include_patterns = assets/**,*.py,*.json,*.txt

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,pygame==2.5.2,pillow

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/splash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/icon.png

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use - deprecated, will be auto-detected

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the manifestplaceholders property.
# This property takes a dictionary of key-value pairs. (via a string)
# Usage example : android.manifest.placeholders = [myCustomUrl:\"org.kivy.customurl\"]
# android.manifest.placeholders = [:]

# (bool) disables the compilation of py to pyc/pyo files when packaging
# android.no-compile-pyo = True

# (str) The format used to package the app for release mode (aab or apk).
android.release_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android URL / git clone directory (if you want to use a specific version)
#p4a.url =

# (str) python-for-android fork to use, defaults to upstream (kivy)
#p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD, must be within p4a.branch
#p4a.commit = HEAD

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1