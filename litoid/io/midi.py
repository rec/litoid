from ..util.has_thread import HasThread
from functools import cache, cached_property
from typing import Callable
import datacls
import mido
import time
from rtmidi import midiutil, MidiIn
SPIN_TIME = 0.003

Message = mido.Message


@cache
def midiin():
    return MidiIn(midiutil.get_api_from_environment())


def get_input_ports():
    return midiin().get_ports()


def open_input_port(input_name):
    midiin, port_name = midiutil.open_midiinput(input_name)
    timer = 0
    try:
        while True:
            while not (msg := midiin.get_message()):
                time.sleep(SPIN_TIME)

            message, deltatime = msg
            timer = timer + deltatime if timer else time.time()
            yield Message.from_bytes(message, time=timer)

    finally:
        midiin.close_port()


@datacls.mutable
class MidoMidiInput(HasThread):
    callback: Callable = print
    name: str = ''

    open_input = staticmethod(mido.open_input)
    get_input_names = staticmethod(mido.get_input_names)

    def _target(self):
        for msg in self.input:
            self.callback(msg)

    @cached_property
    def input_name(self):
        return self.name or sorted(self.get_input_names())[0]

    @cached_property
    def input(self):
        return self.open_input(self.input_name)


@datacls
class MidiOutput:
    name: str | None = None

    @cached_property
    def output_name(self):
        return self.name or sorted(mido.get_output_names()[0])

    @cached_property
    def output(self):
        return mido.open_output(self.name)


class RtMidiInput(MidoMidiInput):
    get_input_names = staticmethod(get_input_ports)
    open_input = staticmethod(open_input_port)


MidiInput = RtMidiInput
