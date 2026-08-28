[app]
title = TikTok Live Reader
package.name = tiktoklivereader
package.domain = org.tiktokreader
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,html
version = 1.0
requirements = python3,kivy,pyjnius,TikTokLive==7.0.0,websockets==15.0.1
android.permissions = INTERNET
android.api = 35
android.minapi = 23
icon.filename = %(source.dir)s/icon.png
orientation = portrait

[buildozer]
log_level = 2
warn_root = 1
