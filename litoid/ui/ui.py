from ..util.thread_queue import ThreadQueue
from functools import cached_property
import PySimpleGUI as sg
import datacls

sg.theme('Material1')


@datacls
class UIDesc:
    font: tuple[str, int] = ('Courier', 18)
    title: str = '💡 Litoid 💡'

    def layout(self):
        raise NotImplementedError


@datacls(slots=True)
class Message:
    key: str
    values: list[str, ...]

    @property
    def is_close(self):
        return self.key in (sg.WIN_CLOSED, 'Cancel')


@datacls
class UI(UIDesc, ThreadQueue):
    def callback(self, msg):
        print(msg)

    @cached_property
    def window(self):
        return sg.Window(self.title, self.layout(), font=self.font)

    def start(self):
        """Must be run on the main thread, blocks until quit"""
        if not super().start():
            while self.running:
                self.put(e := Message(*self.window.read()))
                if e.is_close:
                    self.stop()
                    self.put(None)
