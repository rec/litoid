from litoid.io.midi.message import ControlChange
from litoid.state import scene, state as _state


class MidiScene(scene.Scene):
    def __init__(self, ie):
        self.ie = ie

    def callback(self, state: _state.State, m: object) -> bool:
        if isinstance(m, ControlChange) and m.channel == 0 and m.control < 19:
            d = m.control >= 10
            channel = m.control - d * 10
            value = m.value + 128 * d
            self.ie.set_midi_level(channel, value)
