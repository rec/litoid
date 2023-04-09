from litoid.io.midi_message import ControlChange
from litoid.state import scene, state as _state
import mido


class MidiScene(scene.Scene):
    def __init__(self, ie):
        self.ie = ie

    def callback(self, state: _state.State, m: object) -> bool:
        is_control = (
            (isinstance(m, mido.Message) and m.type == 'control_change')
            or isinstance(m, ControlChange)
        )

        if is_control and m.channel == 0 and (m.control <= 18):
            d = m.control >= 10
            channel = m.control - d * 10
            value = m.value + 128 * d
            self.ie.set_midi_level(channel, value)
