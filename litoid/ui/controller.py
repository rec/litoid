from . import action
from .model import Model
from .view import View
from litoid import log
from litoid.state.scene import CallbackScene
from litoid.io.midi.message import ControlChange
from pathlib import Path
import json


class Controller:
    def __init__(self, path=Path('.')):
        self.view = View(callback=self.callback)
        iname = list(self.view.lamps)[0]
        self.model = Model(iname, path)
        for c in self.view.canvases.values():
            c.draw_recorder(self.model.dmx_recorder)

    @property
    def canvas(self):
        return self.view.canvases[self.iname]

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
        scene = CallbackScene(self._scene_callback)
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
            self.lamp.set_levels(value)
            self.set_levels(self.iname, value)
        else:
            names = sorted(levels)
            log.error(f'Bad instrument: found {self.iname}, expected {names}')

    def set_preset(self, preset_name):
        self.model.selected_preset_name = preset_name
        self.view.update_presets(self.model.iname, value=preset_name)
        self.lamp.set_levels(self.model.selected_preset)
        self.view.update_instrument(
            self.instrument, self.model.selected_preset,
        )

    def blackout(self):
        self.lamp.blackout()
        self.set_levels(self.lamp.levels)

    def set_level(self, ch: int | str, v: int | str, *skip):
        self._set_level(ch, v, *skip)
        self.lamp.send_packet()

    def set_levels(self, d):
        for k, v in d.items():
            self._set_level(k, v)
        self.lamp.send_packet()

    def set_midi_level(self, ch: int, v: int):
        if 0 <= ch < len(self.instrument.channels):
            if self.instrument.channels[ch] in self.instrument.value_names:
                v *= 2
            self.set_level(ch, v)

    def new(self, name):
        if name in self.model.presets:
            log.error('Preset', name, 'exists')
            return

        self.model.presets[name] = dict(self.model.selected_preset)
        values = sorted(self.model.presets)
        self.view.update_presets(self.iname, values=values, value=name)

    def _scene_callback(self, m):
        self.model.callback(m)

        if isinstance(m, ControlChange) and m.channel == 0 and m.control < 19:
            d = m.control >= 10
            channel = m.control - d * 10
            value = m.value + 128 * d
            self.set_midi_level(channel, value)

    def _set_level(self, ch, v, *skip):
        level = self.instrument.map(ch, v)
        self.model.dmx_recorder.record(level.cv, key_size=1)
        self.model.selected_preset[level.channel_name] = level.canonical_value
        self.lamp.set_level(*level.cv)
        self.view.set_level(self.iname, level, *skip)
