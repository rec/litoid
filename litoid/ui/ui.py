from ..util.thread_queue import ThreadQueue
from functools import cached_property
from pathlib import Path
import PySimpleGUI as sg
import datacls

SUFFIX = '.ico'
ICON_PATH = Path(__file__).parents[2] / 'images/tom-swirly.ico'
assert ICON_PATH.exists(), str(ICON_PATH)
sg.theme('Material1')
sg.set_options(icon=str(ICON_PATH))

CLOSERS = sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT


@datacls.mutable
class UIDesc:
    font: tuple[str, int] = ('Courier', 18)
    title: str = '💡 Litoid 💡'
    icon: Path = ICON_PATH

    def layout(self):
        raise NotImplementedError


@datacls(slots=True)
class Message:
    key: str
    values: list[str, ...]

    @property
    def is_close(self):
        return self.key in CLOSERS


@datacls.mutable
class UI(UIDesc, ThreadQueue):
    def callback(self, msg):
        print(msg)

    @cached_property
    def window(self):
        return sg.Window(
            self.title,
            self.layout(),
            font=self.font,
            enable_close_attempted_event=True
        )

    def start(self):
        """Must be run on the main thread, blocks until quit"""
        if not super().start():
            while self.running:
                if msg := self.window.read():
                    self.put(msg := Message(*msg))
                if not msg or msg.is_close:
                    self.stop()
                    self.put(None)
