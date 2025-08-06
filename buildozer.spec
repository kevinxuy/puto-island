[app]
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
warn_on_root = 0