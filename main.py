import asyncio
import json
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
        await asyncio.gather(*[ws.send(payload) for ws in CONNECTED_WEBSOCKETS])

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
        CONNECTED_WEBSOCKETS.remove(websocket)

def run_backend():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(ws_handler, "127.0.0.1", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

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
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True)
        webview.setWebViewClient(WebViewClient())
        # Membuka file index.html lokal
        webview.loadUrl("file:///android_asset/index.html")
        activity.setContentView(webview)

if __name__ == "__main__":
    TikTokLiveApp().run()
