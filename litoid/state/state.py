from . import osc
from functools import cached_property
import datacls


@datacls
class State:
    dmx_port: str = '/dev/cu.usbserial-6AYL2V8Z'

    midi_input_name: str | None = None

    osc_desc: osc.Desc = datacls.field(osc.Desc)

    @cached_property
    def dmx(self):
        from . dmx import DMX

        return DMX(self.dmx_port)

    @cached_property
    def midi_input(self):
        from . midi import MidiInput

        return MidiInput(self.scene.midi_callback, self.midi_input_name)

    @cached_property
    def timed_heap(self):
        from .util.timed_heap import TimedHeap

        return TimedHeap()

    @cached_property
    def scene(self):
        from . scene import SceneHolder

        return SceneHolder(self)

    @cached_property
    def osc_server(self):
        from . osc import Server

        return Server(self.scene.osc_callback, **self.osc_desc.asdict())
