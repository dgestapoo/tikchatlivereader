[app]
title = TikTok Reader
package.name = tiktokreader
package.domain = org.tiktok.reader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html
version = 1.0

# Hanya sertakan modul yang sudah memiliki recipe Android resmi
requirements = python3,kivy,openssl,sqlite3,pyjnius,websockets,certifi,chardet,idna,urllib3,requests,TikTokLive

icon.filename = %(source.dir)s/icon.png
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2
android.ndk = 25b
android.log_filters = *:S python:D
android.copy_libs = 1

android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
