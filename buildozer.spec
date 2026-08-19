[app]

# (str) Title of your application
title = TikTok Reader

# (str) Package name
package.name = tiktokreader

# (str) Package domain (needed for android/ios packaging)
package.domain = org.tiktok.reader

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (include extension to exclude)
source.include_exts = py,png,jpg,kv,atlas,html

# (str) Application versioning
version = 1.0

# (list) Application requirements
# Menghapus asyncio/requests/urllib3 agar tidak bentrok dengan modul internal Python 3 Android
requirements = python3,kivy,openssl,sqlite3,pyjnius,TikTokLive,websockets,certifi,chardet,idna

# (str) Icon of the application (Mengarahkan ke file icon.png di root folder)
icon.filename = %(source.dir)s/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android build tools version to use
android.build_tools_version = 33.0.2

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android logcat filters to use
android.log_filters = *:S python:D

# (bool) Copy library instead of making a lib dir
android.copy_libs = 1

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
