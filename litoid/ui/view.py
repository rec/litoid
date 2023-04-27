from . import defaults, layout, ui
from .drawing_canvas import DrawingCanvas
from ..state.level import Level
from ..state.state import State, make_state
from functools import cached_property
from typing import Callable
import datacls


@datacls.mutable
class View(ui.UI):
    state: State = datacls.field(make_state)
    commands: dict[str, str] = datacls.field(lambda: dict(defaults.COMMANDS))
    callback: Callable = print

    def start(self, scene=None):
        self.state.blackout()
        self.state.midi_input.start()
        self.state.scene = scene

        for key, command in self.commands.items():
            command = command.split()[0].rstrip('.').lower()
            self.window.bind(f'<Command-{key}>', command)

        try:
            super().start()
        finally:
            self.state.scene = None
            self.state.blackout()

    @cached_property
    def canvases(self) -> dict[str, DrawingCanvas]:
        cv = (DrawingCanvas(self.window, i) for i in self.lamps.values())
        return {c.iname: c for c in cv}

    @cached_property
    def lamps(self):
        lamps = {}
        for lamp in self.state.lamps.values():
            lamps.setdefault(lamp.instrument.name, lamp)
        return dict(sorted(lamps.items()))

    def layout(self):
        return [[layout(self.lamps.values())]]

    def set_level(self, iname: str, level: Level, *skip):
        def set_window(action, value):
            if action not in skip:
                key = f'{action}.{iname}.{level.channel_name}'
                self.update(key, value=level.value)

        set_window('input', level.value)
        if level.value_name:
            set_window('combo', level.value_name)
        else:
            set_window('slider', level.value)

    def update(self, key, **kwargs):
        self.window[key].update(**kwargs)

    def update_presets(self, iname, **kwargs):
        self.update(f'preset.{iname}', **kwargs)

    def update_instrument(self, instrument, levels):
        for k, v in levels.items():
            self.set_level(instrument.name, instrument.map(k, v))
