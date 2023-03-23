from ..util.has_thread import HasThread
from typing import Callable
import datacls
import pynput


@datacls
class _Base(HasThread):
    callback: Callable = print

    def _target(self):
        with self.event_module.Events() as events:
            for e in events:
                self.callback(e)


class Keyboard(_Base):
    event_module = pynput.keyboard


class Mouse(_Base):
    event_module = pynput.mouse
