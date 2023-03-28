from ..util.has_thread import HasThread
from typing import Callable
import datacls
import pynput


@datacls
class _Base(HasThread):
    callback: Callable = print

    def _target(self):
        with self.event_module.Events() as events:
            for msg in events:
                self.callback(msg)

    @classmethod
    def Message(cls) -> type:
        return cls.event_module.Events.Event


class Keyboard(_Base):
    event_module = pynput.keyboard


class Mouse(_Base):
    event_module = pynput.mouse
