# TikTok Live Reader

Versi native Android berbasis Kivy. Versi ini tidak menggunakan WebView, HTML, atau WebSocket lokal.

## Fitur

- UI native Kivy
- Koneksi TikTokLive berjalan di thread dan event loop asyncio terpisah
- Update UI selalu dikirim kembali ke thread utama Kivy melalui `Clock`
- Mendukung Android 6+ (API 23), termasuk Android 13/14
- Hanya membutuhkan permission `INTERNET` dan `WAKE_LOCK`

## Build dengan Linux/macOS

Instal Python 3.11, Java 17, Android SDK/NDK, lalu:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install buildozer
buildozer -v android debug
