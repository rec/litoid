from .midi_message import MidiMessage
from ..util.has_thread import HasThread
from functools import cached_property
from typing import Callable
import datacls
import mido
import time
from rtmidi import midiutil, MidiIn
SPIN_TIME = 0.003

if not True:
    make_message = mido.Message.from_bytes
else:
    make_message = MidiMessage


@datacls
class MidiOutput:
    name: str | None = None

    @cached_property
    def output_name(self):
        return self.name or sorted(mido.get_output_names()[0])

    @cached_property
    def output(self):
        return mido.open_output(self.name)


@datacls.mutable
class MidiInput(HasThread):
    callback: Callable = print
    make_message: bool = True
    name: str = ''
    last_event_time: float = 0

    def _target(self):
        midiin, port_name = midiutil.open_midiinput(self.input_name)
        try:
            while True:
                while not (msg := midiin.get_message()):
                    time.sleep(SPIN_TIME)

                mbytes, deltatime = msg
                if self.last_event_time:
                    self.last_event_time += deltatime
                else:
                    # Ignore the first deltatime, which seems to be 0 anyway
                    self.last_event_time = time.time()

                if self.make_message:
                    msg = make_message(mbytes, time=self.last_event_time)
                self.callback(msg)
        finally:
            midiin.close_port()

    @cached_property
    def midiin(self):
        return MidiIn(midiutil.get_api_from_environment())

    def get_input_names(self):
        return self.midiin.get_ports()

    @cached_property
    def input_name(self):
        return self.name or sorted(self.get_input_names())[0]
