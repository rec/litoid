from functools import cached_property
from threading import Thread
from typing import Callable
import datacls
import mido


@datacls
class MidiInput:
    callback: Callable = print
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


@datacls
class MidiOutput:
    name: str | None = None

    @cached_property
    def output(self):
        return mido.open_output(self.name)
