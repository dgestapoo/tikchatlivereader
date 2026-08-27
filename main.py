import os
import json
import asyncio
import threading
import websockets
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, FollowEvent

# Framework GUI Kivy & WebView
from kivy.app import App
from kivy.utils import platform

if platform == 'android':
    from android.runnable import run_on_ui_thread
    from jnius import autoclass
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
else:
    def run_on_ui_thread(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

# --- LOGIKA BACKEND TIKTOK & WEBSOCKET ---
CONNECTED_WEBSOCKETS = set()

async def send_to_html(data_type: str, user: str, message: str = ""):
    if CONNECTED_WEBSOCKETS:
        payload = json.dumps({"type": data_type, "user": user, "message": message})
        # Mengirim data ke seluruh klien WebSocket yang terhubung
        for ws in list(CONNECTED_WEBSOCKETS):
            try:
                await ws.send(payload)
            except Exception:
                pass

async def start_tiktok(username: str):
    if not username.startswith("@"):
        username = "@" + username

    client = TikTokLiveClient(unique_id=username)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        await send_to_html("system", "System", f"Terhubung ke live {event.unique_id}")

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        if len(event.comment) > 1:
            await send_to_html("chat", event.user.nickname, event.comment)

    @client.on(FollowEvent)
    async def on_follow(event: FollowEvent):
        await send_to_html("follow", event.user.nickname, "mengikuti anda")

    try:
        await client.connect()
    except Exception as e:
        await send_to_html("system", "Error", str(e))

async def ws_handler(websocket):
    CONNECTED_WEBSOCKETS.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("action") == "start":
                asyncio.create_task(start_tiktok(data.get("username")))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_WEBSOCKETS.discard(websocket)

async def main_ws():
    async with websockets.serve(ws_handler, "127.0.0.1", 8765):
        await asyncio.Future()  # Menjaga server tetap berjalan

def run_backend():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_ws())

# --- TAMPILAN KIVY / WEBVIEW ---
class TikTokLiveApp(App):
    def build(self):
        # Jalankan Backend Server di Background Thread
        threading.Thread(target=run_backend, daemon=True).start()
        
        if platform == 'android':
            self.start_webview()
        return None

    @run_on_ui_thread
    def start_webview(self):
        webview = WebView(activity)
        settings = webview.getSettings()
        
        # Pengaturan Wajib untuk Komunikasi WebSocket dari file://
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setAllowFileAccess(True)
        settings.setAllowFileAccessFromFileURLs(True)
        settings.setAllowUniversalAccessFromFileURLs(True)
        
        webview.setWebViewClient(WebViewClient())
        
        # Mengambil lokasi absolut file index.html di ruang aplikasi Android
        html_path = os.path.abspath("index.html")
        webview.loadUrl(f"file://{html_path}")
        
        activity.setContentView(webview)

if __name__ == "__main__":
    TikTokLiveApp().run()
