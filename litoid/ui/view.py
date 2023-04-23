from . import canvas_window, defaults, layout, ui
from ..state import instruments
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
        canvas_window.make_figure(self.window)

        for key, command in self.commands.items():
            command = command.split()[0].rstrip('.').lower()
            self.window.bind(f'<Command-{key}>', command)

        try:
            super().start()
        finally:
            self.state.scene = None
            self.state.blackout()

    @cached_property
    def lamps(self):
        lamps = {}
        for lamp in self.state.lamps.values():
            lamps.setdefault(lamp.instrument.name, lamp)
        return dict(sorted(lamps.items()))

    def layout(self):
        return [[layout(self.lamps.values())]]

    def set_level(self, iname: str, channel: int, value: int, *skip):
        instrument = instruments()[iname]
        channel = instrument.channels[channel]
        vname = instrument.level_to_name(channel, value)

        def set_window(action, value):
            if action not in skip:
                self.update(f'{action}.{iname}.{channel}', value=value)

        set_window('input', value)
        if vname:
            set_window('combo', vname)
        else:
            set_window('slider', value)

    def update(self, key, **kwargs):
        self.window[key].update(**kwargs)

    def update_presets(self, iname, **kwargs):
        self.update(f'preset.{iname}', **kwargs)

    def update_instrument(self, iname, levels):
        for k, v in levels.items():
            self.set_level(iname, k, v)
