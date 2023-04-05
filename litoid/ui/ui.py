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
LITOID_CLOSE = 'litoid.(none).close'

CLOSERS = sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, LITOID_CLOSE
HAS_FOCUS = 'has.(none).focus'
NO_FOCUS = 'no.(none).focus'


@datacls.mutable
class UIDesc:
    font: tuple[str, int] = ('Courier', 18)
    title: str = '💡 Litoid 💡'
    icon: Path = ICON_PATH

    def layout(self):
        raise NotImplementedError


@datacls
class Message:
    """
    All message keys look like name.channel.action
    OR (soon) name.action
    """
    key: str
    values: list[str, ...] | None = None

    @property
    def is_close(self):
        return self.key in CLOSERS

    @cached_property
    def name(self):
        name, channel, action = self.key.split('.')
        return name

    @cached_property
    def channel(self):
        name, channel, action = self.key.split('.')
        return channel

    @cached_property
    def action(self):
        """Return the name of the action"""
        name, channel, action = self.key.split('.')
        return action


@datacls.mutable
class UI(UIDesc, ThreadQueue):
    has_focus = False

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
        w.bind('<FocusIn>', HAS_FOCUS)
        w.bind('<FocusOut>', NO_FOCUS)

        return w

    def quit(self):
        self.window.write_event_value(LITOID_CLOSE, None)

    def start(self):
        """Must be run on the main thread, blocks until quit"""
        if r := super().start():
            return r

        while self.running:
            if raw_msg := self.window.read():
                self.put(msg := Message(*raw_msg))

            if not msg or msg.is_close:
                self.stop()
                self.put(None)
