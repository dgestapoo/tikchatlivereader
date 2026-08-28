# TikTok Live Reader

Aplikasi Android berbasis Kivy dengan frontend HTML/WebView.

## Arsitektur

```text
TikTok Live
    ↓
TikTokLiveClient (main.py)
    ↓
WebSocket lokal
127.0.0.1:8765
    ↓
index.html / WebView
    ↓
Tampilan chat + Text-to-Speech
```

Server WebSocket lokal adalah bagian dari desain aplikasi dan berjalan di perangkat Android yang sama.

## Build lokal

```bash
buildozer -v android debug
```

APK akan dibuat di:

```text
bin/
```

## GitHub Actions

### Debug

Push ke branch `main` atau `master` akan menjalankan:

```text
.github/workflows/build-check.yml
.github/workflows/build-apk.yml
```

APK debug tersedia pada bagian **Artifacts** dari workflow `Build Android APK`.

### Release

Buat tag versi:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Workflow release akan membangun APK dan membuat GitHub Release.

> Catatan: workflow release di atas menghasilkan APK unsigned/universal release. Untuk distribusi Play Store, tambahkan signing keystore melalui GitHub Secrets.
