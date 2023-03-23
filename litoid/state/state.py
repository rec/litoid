from ..util.read_write import ReadWrite
from ..io import osc
from functools import cached_property
import datacls


@datacls
class State(ReadWrite):
    dmx_port: str = '/dev/cu.usbserial-6AYL2V8Z'
    lamp_descs: list = datacls.field(list)
    midi_input_name: str | None = None
    osc_desc: osc.Desc = datacls.field(osc.Desc)

    @cached_property
    def dmx(self):
        from .dmx import DMX

        return DMX(self.dmx_port)

    @cached_property
    def keyboard(self):
        from .key_mouse import Keyboard

        return Keyboard(self.scene.callback)

    @cached_property
    def lamps(self):
        from .lamps import Lamps

        return Lamps(self.dmx, self.lamp_descs)

    @cached_property
    def midi_input(self):
        from .midi import MidiInput

        return MidiInput(self.scene.midi_callback, self.midi_input_name)

    @cached_property
    def mouse(self):
        from .key_mouse import Mouse

        return Mouse(self.scene.callback)

    @cached_property
    def osc_server(self):
        from .osc import Server

        return Server(self.scene.osc_callback, **self.osc_desc.asdict())

    @cached_property
    def timed_heap(self):
        from .util.timed_heap import TimedHeap

        return TimedHeap()

    @cached_property
    def scene(self):
        from .scene import SceneHolder

        return SceneHolder(self)

    def start_all(self):
        self.dmx  # .start()
        self.keyboard.start()
        self.lamps
        self.midi_input.start()
        self.mouse.start()
        self.osc_server.start()
        self.timed_heap.start()
