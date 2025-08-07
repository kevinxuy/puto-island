[app]
title = Puto Island
package.name = putoisland
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,txt,json
version = 0.1
requirements = python3,pygame2
orientation = portrait
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 28

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Bootstrap to use for android builds
p4a.bootstrap = pygame

# (list) The Android archs to build for
android.archs = armeabi-v7a

[buildozer]
log_level = 2