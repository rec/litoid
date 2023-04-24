from ..util.is_running import IsRunning
from .event import Event
from functools import cached_property
from litoid import log
from pathlib import Path
import PySimpleGUI as sg
import datacls

SUFFIX = '.ico'
ICON_PATH = Path(__file__).parents[2] / 'images/tom-swirly.ico'
LITOID_CLOSE = 'request_close'

assert ICON_PATH.exists(), str(ICON_PATH)
sg.theme('Material1')
sg.set_options(icon=str(ICON_PATH))


@datacls.mutable
class UIDesc:
    font: tuple[str, int] = ('Courier', 18)
    title: str = '💡 Litoid 💡'
    icon: Path = ICON_PATH


@datacls.mutable
class UI(UIDesc, IsRunning):
    windows: dict = datacls.field(dict)

    def callback(self, msg):
        print('UI.callback', msg)

    def make_window(self, title=None, layout=None, font=None, quit=None):
        assert title not in self.windows
        self.windows[title] = sg.Window(
            title or self.title,
            layout or self.layout(),
            enable_close_attempted_event=bool(quit),
            finalize=True,
            font=font or self.font,
        )
        if quit:
            sg.Window.hidden_master_root.createcommand('tk::mac::Quit', quit)
        return self.windows[title]

    @cached_property
    def window(self):
        return self.make_window(quit=self.quit)

    def quit(self):
        log.debug('quit')
        self.window.write_event_value(LITOID_CLOSE, None)

    def yes_no_cancel(self, title, messages):
        popup = sg.Window(
            title,
            [
                *([sg.T(m)] for m in messages),
                [sg.Yes(s=10), sg.No(s=10), sg.Cancel(s=15)]
            ],
            disable_close=True)
        choice, _ = popup.read(close=True)
        return choice

    def _start(self):
        """Must be run on the main thread, blocks until quit"""
        super()._start()
        while self.running:
            if raw_msg := sg.read_all_windows():
                self.callback(Event(*raw_msg))
            else:
                self.stop()
