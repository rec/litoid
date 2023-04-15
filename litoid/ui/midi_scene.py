from litoid.io.midi.message import ControlChange, MidiMessage
from litoid.io.midi.recorder import MidiRecorder
from litoid.state import scene
from litoid.state.state import State
import numpy as np


class MidiScene(scene.Scene):
    def __init__(self, controller, path=None):
        self.controller = controller
        self.path = path
        self.recorder = MidiRecorder()

    def callback(self, state: State, m: object) -> bool:
        if not isinstance(m, MidiMessage):
            return

        if isinstance(m, ControlChange) and m.channel == 0 and m.control < 19:
            d = m.control >= 10
            channel = m.control - d * 10
            value = m.value + 128 * d
            self.controller.set_midi_level(channel, value)

        self.recorder.record(m)

    def unload(self, state: State):
        if self.path:
            np.savez(self.path, self.recorder.asdict())
