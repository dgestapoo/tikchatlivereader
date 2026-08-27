[app]

# (str) Title of your application
title = TikTok Reader

# (str) Package name
package.name = tiktokreader

# (str) Package domain (needed for android packaging)
package.domain = org.tiktok.reader

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (process only files with these extensions)
source.include_exts = py,png,jpg,kv,atlas,html

# (str) Application versioning
version = 1.0

# (list) Application requirements
# Library wajib untuk TikTokLive, Kivy, dan WebView
requirements = python3,kivy,openssl,sqlite3,pyjnius,websockets,certifi,chardet,idna,TikTokLive

# (str) Supported orientations (portrait, landscape, sensorPortrait, sensorLandscape)
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 31

# (int) Minimum Android API supported
android.minapi = 21

# (str) Android Build Tools version
android.build_tools_version = 31.0.0

# (str) Android NDK version
android.ndk = 25b

# (bool) Copy libraries instead of symlinking
android.copy_libs = 1

# (str) Python-for-android branch
p4a.branch = master

# (list) Supported architectures (arm64-v8a untuk HP Android modern)
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
