from . import action, midi_scene
from .model import Model
from .view import View
from .. import log
import json
import time


class Controller:
    def __init__(self):
        self.view = View(callback=self.callback)
        iname = list(self.view.lamps)[0]
        self.model = Model(iname)

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
        scene = midi_scene.MidiScene(self, 'midi.npz')
        self.view.start(scene)

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
            self.set_levels(self.iname, value)
        else:
            names = sorted(levels)
            log.error(f'Bad instrument: found {self.iname}, expected {names}')

    def set_preset(self, preset_name):
        self.model.selected_preset_name = preset_name
        self.view.update_presets(self.model.iname, value=preset_name)
        self.lamp.levels = self.model.selected_preset
        self.view.update_instrument(
            self.model.iname, self.model.selected_preset
        )

    def blackout(self):
        self.lamp.blackout()
        self.set_levels(self.lamp.levels)

    def set_level(self, ch, v, *skip):
        self._set_level(ch, v, *skip)
        self.lamp.render()

    def set_levels(self, d):
        for k, v in d.items():
            self._set_level(k, v)
        self.lamp.render()

    def set_midi_level(self, ch, v):
        if ch < len(self.lamp):
            if self.instrument.channels[ch] in self.instrument.value_names:
                v *= 2
            self.set_level(ch, v)

    def _set_level(self, ch, v, *skip):
        self.lamp[ch] = v
        self.view.set_level(self.iname, ch, v, *skip)
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
        Controller().start()
    finally:
        time.sleep(0.1)  # Allow daemon threads to print tracebacks


if __name__ == "__main__":
    main()
