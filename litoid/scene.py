from . dmx import DMX
from . midi import MidiInput
from . timed_heap import TimedHeap
from functools import cached_property
import datacls


@datacls
class Universe:
    dmx_port: str
    midi_input_name: str | None = None
    timed_heap: TimedHeap = datacls.field(TimedHeap)

    @cached_property
    def dmx(self):
        return DMX(self.dmx_port)

    @cached_property
    def midi_input(self):
        return MidiInput(self.midi_input_name)


@datacls
class Scene:
    pass
