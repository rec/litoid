from . import action
from . view import View
from ..io import midi
from ..state import instruments, scene, state as _state
from ..util.play import play_error
from functools import cached_property
import copy
import datacls


@datacls.mutable
class Model:
    current_instrument: str

    @cached_property
    def all_presets(self):
        return {k: copy.deepcopy(v.presets) for k, v in instruments().items()}

    @cached_property
    def current_presets(self):
        return {k: None for k in self.all_presets}


@datacls
class Controller:
    model: Model
    view: View

    @classmethod
    def make(cls):
        view = View()
        model = Model(list(view.lamps)[0])
        cont = cls(model, view)
        view.callback = cont.callback
        return cont

    @property
    def iname(self):
        return self.instrument.name

    @property
    def instrument(self):
        return self.lamp.instrument

    @property
    def lamp(self):
        return self.view.lamps[self.model.current_instrument]

    def start(self):
        self.view.state.scene = MidiScene(self)
        self.view.start()

    def callback(self, msg):
        return action.Action(self, msg)()

    def copy(self):
        return {self.iname: self.lamp.levels}

    def paste(self, levels):
        if value := levels.get(self.iname):
            self.lamp.levels = value
            self.set_channel_levels(self.iname, value)
            return True
        else:
            play_error(f'Wrong instrument {levels}')

    def set_preset(self, name):
        # BROKEN
        if preset := self.all_presets.get(self.iname, {}).get(name):
            for ch in self.instrument.channels:
                self.set_address_value(ch, preset[ch])  # NO
        else:
            play_error(f'No preset named {name}')

    def blackout(self):
        self.lamp.blackout()
        self.set_channel_levels(self.iname, self.lamp.levels)

    def set_channel_level(self, iname, ch, v):
        self.lamp[ch] = v
        self.view.set_channel_strip(iname, ch, v)

    def set_channel_levels(self, iname, d):
        for k, v in d.items():
            self.set_channel_level(iname, k, v)

    def set_midi_level(self, ch, v, scale_name=False):
        if ch < len(self.lamp):
            if scale_name:
                if self.instrument.channels[ch] in self.instrument.value_names:
                    v *= 2
            self.set_channel_level(self.iname, ch, v)


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
            self.ie.set_midi_level(channel, value, scale_name=True)


def main():
    try:
        app = Controller.make()
        app.start()
    finally:
        import time
        time.sleep(0.1)


if __name__ == "__main__":
    main()
