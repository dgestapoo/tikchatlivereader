import asyncio
import json
import threading
from typing import Optional

import websockets
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, FollowEvent

from kivy.app import App
from kivy.utils import platform

if platform == "android":
    from android.runnable import run_on_ui_thread
    from jnius import autoclass
    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
else:
    def run_on_ui_thread(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

WS_HOST = "127.0.0.1"
WS_PORT = 8765

connected_websockets = set()
tiktok_task: Optional[asyncio.Task] = None
tiktok_client: Optional[TikTokLiveClient] = None

async def send_to_html(data_type: str, user: str = "", message: str = "") -> None:
    if not connected_websockets:
        return

    payload = json.dumps({
        "type": data_type,
        "user": user,
        "message": message,
    }, ensure_ascii=False)

    sockets = list(connected_websockets)

    async def send_one(ws):
        try:
            await ws.send(payload)
        except Exception:
            connected_websockets.discard(ws)

    await asyncio.gather(*(send_one(ws) for ws in sockets))


def normalize_username(username: str) -> str:
    username = (username or "").strip()
    return username if username.startswith("@") else f"@{username}"


async def stop_tiktok() -> None:
    global tiktok_task, tiktok_client

    client = tiktok_client
    task = tiktok_task
    tiktok_client = None
    tiktok_task = None

    if client is not None:
        try:
            await client.disconnect()
        except Exception:
            pass

    if task is not None and task is not asyncio.current_task():
        if not task.done():
            task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception:
            pass


async def start_tiktok(username: str) -> None:
    global tiktok_task, tiktok_client

    username = normalize_username(username)
    if username == "@":
        await send_to_html("system", "System", "Username TikTok belum diisi.")
        return

    await stop_tiktok()

    client = TikTokLiveClient(unique_id=username)
    tiktok_client = client
    current_task = asyncio.current_task()
    tiktok_task = current_task

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        await send_to_html("system", "System", f"Terhubung ke live {event.unique_id}")

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        comment = (event.comment or "").strip()
        nickname = getattr(event.user, "nickname", "") or "Unknown"
        if comment:
            await send_to_html("chat", nickname, comment)

    @client.on(FollowEvent)
    async def on_follow(event: FollowEvent):
        nickname = getattr(event.user, "nickname", "") or "Unknown"
        await send_to_html("follow", nickname, "mengikuti anda")

    @client.on(DisconnectEvent)
    async def on_disconnect(_: DisconnectEvent):
        await send_to_html("system", "System", f"Koneksi live {username} terputus.")

    try:
        await client.connect()
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await send_to_html("system", "Error", f"Gagal terhubung ke {username}: {exc}")
    finally:
        if tiktok_client is client:
            tiktok_client = None
        if tiktok_task is current_task:
            tiktok_task = None


async def ws_handler(websocket) -> None:
    connected_websockets.add(websocket)
    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                await send_to_html("system", "Error", "Pesan dari WebView bukan JSON yang valid.")
                continue

            action = data.get("action")
            if action == "start":
                username = str(data.get("username", "")).strip()
                if not username:
                    await send_to_html("system", "System", "Masukkan username TikTok terlebih dahulu.")
                    continue
                asyncio.create_task(start_tiktok(username))
            elif action == "stop":
                await stop_tiktok()
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as exc:
        print(f"WebSocket handler error: {exc}")
    finally:
        connected_websockets.discard(websocket)


async def backend_main() -> None:
    async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
        print(f"Local WebSocket server: ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()


def run_backend() -> None:
    try:
        asyncio.run(backend_main())
    except Exception as exc:
        print(f"Backend stopped: {exc}")


class TikTokLiveApp(App):
    def build(self):
        self.backend_thread = threading.Thread(
            target=run_backend,
            name="TikTokBackend",
            daemon=True,
        )
        self.backend_thread.start()

        if platform == "android":
            self.start_webview()
        return None

    @run_on_ui_thread
    def start_webview(self):
        webview = WebView(activity)
        settings = webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        webview.setWebViewClient(WebViewClient())
        webview.loadUrl("file:///android_asset/index.html")
        activity.setContentView(webview)


if __name__ == "__main__":
    TikTokLiveApp().run()
