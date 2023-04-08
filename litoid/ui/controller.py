from . import action, midi_scene
from .model import Model
from .view import View
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
        self.view.state.scene = midi_scene.MidiScene(self)
        self.view.start()

    def callback(self, msg):
        log.debug(msg.key)
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
            self.set_channel_levels(self.iname, value)
            return

        log.error(
            'Bad instrument: found', self.iname, 'expected', *sorted(levels)
        )

    def set_preset(self, preset_name):
        self.model.selected_preset_name = preset_name
        self.view.update_presets(self.model.iname, value=preset_name)
        self.view.update_instrument(self.model.iname, self.lamp.levels)

    def blackout(self):
        self.lamp.blackout()
        self.set_channel_levels(self.lamp.levels)

    def set_channel_level(self, ch, v, *skip):
        self._set_channel_level(ch, v, *skip)
        self.lamp.render()

    def set_channel_levels(self, d):
        for k, v in d.items():
            self.set_channel_level(k, v)
        self.lamp.render()

    def set_midi_level(self, ch, v):
        if ch < len(self.lamp):
            if self.instrument.channels[ch] in self.instrument.value_names:
                v *= 2
            self.set_channel_level(ch, v)

    def _set_channel_level(self, ch, v, *skip):
        self.lamp[ch] = v
        self.view.set_channel_strip(self.iname, ch, v, *skip)
        if sp := self.model.selected_preset:
            sp[ch] = v

    def new(self, name):
        if name in self.model.presets:
            log.error('Preset', name, 'exists')
            return

        self.model.presets[name] = self.lamp.levels
        values = sorted(self.model.presets)
        self.view.update_presets(self.iname, values=values, value=name)


def main():
    try:
        app = Controller.make()
        app.start()
    finally:
        import time
        time.sleep(0.1)


if __name__ == "__main__":
    main()
