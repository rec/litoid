from . import lamp
from ..io import dmx, key_mouse, midi, osc
from ..util import file, is_running, read_write, timed_heap
from functools import cached_property, wraps
from pathlib import Path
import datacls
import time
import xmod

SPIN_TIME = 0.05
STATE_FILE = Path(__file__).parents[2] / 'state.toml'
assert STATE_FILE.exists()


@datacls.mutable
class State(read_write.ReadWrite, is_running.IsRunning):
    dmx_port: str
    lamp_descs: dict
    osc_desc: dict
    midi_input_name: str | None = None

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
        if self.midi_input_name:
            return midi.MidiInput(self.callback, self.midi_input_name)

    @cached_property
    def mouse(self):
        return key_mouse.Mouse(self.callback)

    @cached_property
    def osc_server(self):
        return osc.Server(callback=self.callback, **self.osc_desc)

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

    @scene.setter
    def scene(self, scene):
        self._scene_holder.scene = scene

    def _start(self):
        if self.use_mouse:
            self.mouse.start()
        else:
            self.keyboard.start()
        self.lamps
        self.midi_input and self.midi_input.start()
        self.osc_server.start()
        self.timed_heap.start()

    def run(self):
        # TODO: deprecated
        s = self.start()
        assert not s, 'Another instance is running'
        try:
            while self.running:
                time.sleep(SPIN_TIME)
        finally:
            self.blackout()

    def blackout(self):
        for la in self.lamps.values():
            la.blackout()

    def callback(self, msg):
        return self.scene.callback(self, msg)


@xmod
@wraps(State)
def state(path: Path | None = None, **kwargs):
    return State(**file.load(path or STATE_FILE), **kwargs)


if __name__ == '__main__':
    State().run()
