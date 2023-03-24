from . import lamp
from ..io import dmx, key_mouse, midi, osc
from ..util import read_write, timed_heap
from functools import cached_property
import datacls


@datacls
class State(read_write.ReadWrite):
    dmx_port: str = '/dev/cu.usbserial-6AYL2V8Z'
    lamp_descs: list = datacls.field(list)
    midi_input_name: str | None = None
    osc_desc: osc.Desc = datacls.field(osc.Desc)

    @cached_property
    def dmx(self):
        return dmx.DMX(self.dmx_port)

    @cached_property
    def keyboard(self):
        return key_mouse.Keyboard(self.scene.callback)

    @cached_property
    def lamps(self):
        return lamp.Lamps(self.dmx, self.lamp_descs)

    @cached_property
    def midi_input(self):
        return midi.MidiInput(self.scene.callback, self.midi_input_name)

    @cached_property
    def mouse(self):
        return key_mouse.Mouse(self.scene.callback)

    @cached_property
    def osc_server(self):
        return osc.Server(
            callback=self.scene.callback, **self.osc_desc.asdict()
        )

    @cached_property
    def timed_heap(self):
        return timed_heap.TimedHeap()

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
        self.scene
