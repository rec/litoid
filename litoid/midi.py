from contextlib import contextmanager
from functools import cached_property, wraps
from pathlib import Path
from threading import Thread
import datacls
import mido
import xmod


@dataclass
class Midi:
    callback: Callable
    name: str | None = None

    @cached_property
    def thread(self):
        return Thread(target=self._target, daemon=True)

    def _target(self):
        for msg in self.input:
            self.callback(msg)

    @cached_property
    def input(self):
        return mido.open_input(self.name)
