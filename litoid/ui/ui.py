from . message import Message
from ..util.is_running import IsRunning
from functools import cached_property
from pathlib import Path
import PySimpleGUI as sg
import datacls

SUFFIX = '.ico'
ICON_PATH = Path(__file__).parents[2] / 'images/tom-swirly.ico'
assert ICON_PATH.exists(), str(ICON_PATH)
sg.theme('Material1')
sg.set_options(icon=str(ICON_PATH))


@datacls.mutable
class UIDesc:
    font: tuple[str, int] = ('Courier', 18)
    title: str = '💡 Litoid 💡'
    icon: Path = ICON_PATH

    def layout(self):
        raise NotImplementedError


@datacls.mutable
class UI(UIDesc, IsRunning):
    def callback(self, msg):
        print('UI.callback', msg)

    @cached_property
    def window(self):
        w = sg.Window(
            self.title,
            self.layout(),
            enable_close_attempted_event=True,
            finalize=True,
            font=self.font,
        )
        sg.Window.hidden_master_root.createcommand('tk::mac::Quit', self.quit)
        return w

    def quit(self):
        self.window.write_event_value(Message.LITOID_CLOSE, None)

    def _start(self):
        """Must be run on the main thread, blocks until quit"""
        super()._start()
        while self.running:
            if raw_msg := self.window.read():
                self.callback(msg := Message(*raw_msg))

            if not msg or msg.is_close:
                self.stop()
