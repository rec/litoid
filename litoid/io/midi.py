from ..util.has_thread import HasThread
from functools import cached_property
from typing import Callable
import datacls
import mido


@datacls
class MidiInput(HasThread):
    callback: Callable = print
    name: str | None = None

    def _target(self):
        for msg in self.input:
            self.callback(msg)

    @cached_property
    def input_name(self):
        return self.name or sorted(mido.get_input_names())[0]

    @cached_property
    def input(self):
        return mido.open_input(self.input_name)


@datacls
class MidiOutput:
    name: str | None = None

    @cached_property
    def output_name(self):
        return self.name or sorted(mido.get_output_names()[0])

    @cached_property
    def output(self):
        return mido.open_output(self.name)
