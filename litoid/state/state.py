from . import lamp
from ..io import dmx, key_mouse, midi, osc
from ..util import is_running, read_write, timed_heap
from functools import cached_property, wraps
from pathlib import Path
import datacls
import time
import tomllib
import xmod

SPIN_TIME = 0.05
STATE_FILE = Path(__file__).parents[2] / 'state.toml'
assert STATE_FILE.exists()


@datacls
class State(read_write.ReadWrite, is_running.IsRunning):
    dmx_port: str = '/dev/cu.usbserial-6AYL2V8Z'
    lamp_descs: list = datacls.field(list)
    midi_input_name: str | None = 'nanoKONTROL SLIDER/KNOB'
    osc_desc: osc.Desc = datacls.field(osc.Desc)

    # Can't use both mouse and keyboard: https://github.com/rec/litoid/issues/5
    use_mouse = False

    @cached_property
    def dmx(self):
        return dmx.DMX(self.dmx_port)

    @cached_property
    def keyboard(self):
        return key_mouse.Keyboard(self.callback)

    @cached_property
    def lamps(self):
        return lamp.lamps(self.dmx, self.lamp_descs)

    @cached_property
    def midi_input(self):
        return midi.MidiInput(self.callback, self.midi_input_name)

    @cached_property
    def mouse(self):
        return key_mouse.Mouse(self.callback)

    @cached_property
    def osc_server(self):
        return osc.Server(callback=self.callback, **self.osc_desc.asdict())

    @cached_property
    def timed_heap(self):
        return timed_heap.TimedHeap()

    @cached_property
    def _scene_holder(self):
        from .scene import SceneHolder

        return SceneHolder(self)

    @property
    def scene(self):
        return self._scene_holder.scene

    def set_scene(self, scene):
        self._scene_holder.set_scene(scene)

    def start(self):
        if self.use_mouse:
            self.mouse.start()
        else:
            self.keyboard.start()
        self.lamps
        self.midi_input.start()
        self.osc_server.start()
        self.timed_heap.start()
        super().start()

    def run(self):
        self.start()
        while self.running:
            time.sleep(SPIN_TIME)

    def callback(self, msg):
        return self.scene.callback(self, msg)


@xmod
@wraps(State)
def state(**kwargs):
    state = tomllib.loads(STATE_FILE.read_text()) | kwargs
    return State(**state)


if __name__ == '__main__':
    State().run()
