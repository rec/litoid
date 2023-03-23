from functools import cached_property
from typing import Callable
import datacls
import pynput
import threading


@datacls
class _Base:
    callback: Callable = print

    @cached_property
    def thread(self):
        return threading.Thread(target=self.target, daemon=True)

    def __post_init__(self):
        self.thread.start()

    def target(self):
        with self.event_module.Events() as events:
            for e in events:
                self.callback(e)


class Keyboard(_Base):
    event_module = pynput.keyboard


class Mouse(_Base):
    event_module = pynput.mouse
