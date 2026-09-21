[app]
title = TikTok Live Reader
package.name = tiktoklivereader
package.domain = org.tiktokreader
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.1,TikTokLive==7.0.0
android.permissions = INTERNET,WAKE_LOCK
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
icon.filename = %(source.dir)s/icon.png
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_root = 1
