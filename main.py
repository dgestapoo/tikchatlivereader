import asyncio
import threading
from typing import Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent, DisconnectEvent, FollowEvent


class ChatRow(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.text_size = (None, None)
        self.padding = (dp(10), dp(8))
        self.bind(width=self._update_text_size, texture_size=self._update_height)

    def _update_text_size(self, *_):
        self.text_size = (max(0, self.width - dp(20)), None)

    def _update_height(self, *_):
        self.height = max(dp(38), self.texture_size[1] + dp(16))


class TikTokReaderService:
    def __init__(self, on_event):
        self.on_event = on_event
        self.thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.client: Optional[TikTokLiveClient] = None
        self.stop_event = threading.Event()
        self.username = ""

    def start(self, username: str) -> bool:
        if self.thread and self.thread.is_alive():
            return False
        self.username = username.strip().lstrip("@").strip()
        if not self.username:
            return False
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run_thread, name="TikTokLive", daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.stop_event.set()
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)

    def _run_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connect())
        finally:
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
            if pending:
                self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self.loop.close()
            self.loop = None
            self.client = None

    async def _disconnect(self):
        if self.client is not None:
            try:
                await self.client.disconnect()
            except Exception:
                pass

    async def _connect(self):
        self.client = TikTokLiveClient(unique_id=self.username)
        display_name = f"@{self.username}"

        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            self.emit("status", f"Terhubung ke live {display_name}")

        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            comment = (event.comment or "").strip()
            nickname = getattr(event.user, "nickname", "") or "Unknown"
            if comment:
                self.emit("chat", f"{nickname}: {comment}")

        @self.client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            nickname = getattr(event.user, "nickname", "") or "Unknown"
            self.emit("follow", f"{nickname} mengikuti Anda")

        @self.client.on(DisconnectEvent)
        async def on_disconnect(_: DisconnectEvent):
            self.emit("status", f"Koneksi {display_name} terputus")

        try:
            await self.client.connect()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.emit("error", f"Gagal terhubung ke {display_name}: {exc}")

    def emit(self, kind: str, message: str):
        Clock.schedule_once(lambda _dt: self.on_event(kind, message), 0)


class TikTokReaderApp(App):
    status = StringProperty("Siap")

    def build(self):
        Window.softinput_mode = "below_target"
        self.service = TikTokReaderService(self.handle_service_event)

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        title = Label(text="[b]TikTok Live Reader[/b]", markup=True, font_size="22sp", size_hint_y=None, height=dp(48))
        root.add_widget(title)

        form = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.username_input = TextInput(hint_text="Username TikTok, contoh: @username", multiline=False, write_tab=False)
        self.username_input.bind(on_text_validate=lambda *_: self.start_reader())
        form.add_widget(self.username_input)
        self.start_button = Button(text="Mulai", size_hint_x=None, width=dp(92))
        self.start_button.bind(on_release=lambda *_: self.start_reader())
        form.add_widget(self.start_button)
        self.stop_button = Button(text="Berhenti", size_hint_x=None, width=dp(92), disabled=True)
        self.stop_button.bind(on_release=lambda *_: self.stop_reader())
        form.add_widget(self.stop_button)
        root.add_widget(form)

        self.status_label = Label(text=self.status, color=(0.4, 0.9, 0.5, 1), size_hint_y=None, height=dp(32), halign="left", valign="middle")
        self.status_label.bind(size=lambda *_: setattr(self.status_label, "text_size", self.status_label.size))
        root.add_widget(self.status_label)

        scroll = ScrollView(do_scroll_x=False)
        self.chat_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        self.chat_box.bind(minimum_height=self.chat_box.setter("height"))
        scroll.add_widget(self.chat_box)
        root.add_widget(scroll)
        self.scroll = scroll
        return root

    def start_reader(self):
        username = self.username_input.text.strip()
        if not username:
            self.handle_service_event("error", "Masukkan username TikTok terlebih dahulu.")
            return
        if self.service.start(username):
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.username_input.disabled = True
            self.handle_service_event("status", f"Menghubungkan ke @{username.lstrip('@')}...")

    def stop_reader(self):
        self.service.stop()
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.username_input.disabled = False
        self.handle_service_event("status", "Koneksi dihentikan")

    def handle_service_event(self, kind: str, message: str):
        self.status = message if kind in ("status", "error") else self.status
        self.status_label.text = self.status
        if kind == "error":
            self.add_row("ERROR", message, (1, 0.35, 0.35, 1))
        elif kind == "chat":
            self.add_row("CHAT", message, (1, 1, 1, 1))
        elif kind == "follow":
            self.add_row("FOLLOW", message, (0.5, 0.85, 1, 1))

    def add_row(self, prefix: str, message: str, color):
        row = ChatRow(text=f"[{prefix}] {message}", color=color)
        self.chat_box.add_widget(row)
        Clock.schedule_once(lambda _dt: setattr(self.scroll, "scroll_y", 0), 0)

    def on_stop(self):
        self.service.stop()


if __name__ == "__main__":
    TikTokReaderApp().run()
