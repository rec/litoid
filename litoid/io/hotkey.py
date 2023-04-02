from ..util.has_thread import HasThread
from functools import cached_property, partial
from pynput import keyboard
from typing import Callable
import datacls


@datacls
class HotKeys(HasThread):
    keys: dict[str, str] = datacls.field(dict)
    callback: Callable = print

    @cached_property
    def hotkeys(self):
        keys = {k: partial(self.callback, v) for k, v in self.keys.items()}
        return keyboard.GlobalHotKeys(keys)

    def _target(self):
        with self.hotkeys as h:
            h.join()


if __name__ == '__main__':
    s = 'abcdefghijklmnopqrstuvwxyz'
    keys = [f'<ctrl>+{i}' for i in s]
    HotKeys(keys)._target()
