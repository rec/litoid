from ..io import midi
from ..state import scene, state as _state


class MidiScene(scene.Scene):
    def __init__(self, ie):
        self.ie = ie

    def callback(self, state: _state.State, m: object) -> bool:
        if (
            isinstance(m, midi.Message)
            and m.type == 'control_change'
            and m.channel == 0
            and (m.control <= 18)  # or 50 <= m.control <= 68)
        ):
            d = m.control >= 10
            channel = m.control - d * 10
            value = m.value + 128 * d
            self.ie.set_midi_level(channel, value)
