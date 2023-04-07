from . import action
from .model import Model
from .view import View
from ..io import midi
from ..state import scene, state as _state
from .. import log
import datacls
import json


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
        return self.view.lamps[self.model.iname]

    def start(self):
        self.view.state.scene = MidiScene(self)
        self.view.start()

    def callback(self, msg):
        print('Controller.callback', msg.key)
        return action.Action(self, msg)()

    def copy(self) -> str:
        return json.dumps({self.iname: self.lamp.levels})

    def paste(self, levels: str):
        try:
            levels = json.loads(levels)
        except Exception:
            log.error('Bad JSON in cut buffer')
            return

        if value := levels.get(self.iname):
            self.lamp.levels = value
            self.set_channel_levels(iname, value)
            return

        log.error('Bad instrument: found', iname, 'expected', *sorted(levels))

    def set_preset(self, name):
        # BROKEN
        if preset := self.all_presets.get(self.iname, {}).get(name):
            for ch in self.instrument.channels:
                self.set_address_value(ch, preset[ch])  # NO
        else:
            log.error(f'No preset named {name}')

    def blackout(self, iname=None):
        iname = iname or self.model.iname
        lamp = self.view.lamps[iname]
        lamp.blackout()
        self.set_channel_levels(iname, lamp.levels)

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
