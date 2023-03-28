from ..util.thread_queue import ThreadQueue
from functools import cached_property
from typing import Callable
import PySimpleGUI as sg
import datacls

sg.theme('DarkAmber')


@datacls
class UIDesc:
    font: tuple[str, int] = ('Helvetica', 18)
    title: str = '💡 Litoid 💡'

    def layout(self):
        raise NotImplementedError


@datacls(slots=True)
class Message:
    event: str
    values: list[str, ...]

    @property
    def is_close(self):
        return self.event in (sg.WIN_CLOSED, 'Cancel')


@datacls
class UI(UIDesc, ThreadQueue):
    callback: Callable = print

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
