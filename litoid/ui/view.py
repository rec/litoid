from . import defaults, layout_tabgroup, ui
from ..state import instruments, state as _state
from functools import cached_property
from typing import Callable
import datacls


@datacls.mutable
class View(ui.UI):
    state: _state.State = datacls.field(_state)
    commands: dict[str, str] = datacls.field(lambda: dict(defaults.COMMANDS))
    callback: Callable = print

    def start(self):
        self.state.blackout()
        self.state.midi_input.start()

        for key, command in self.commands.items():
            command = command.split()[0].rstrip('.').lower()
            self.window.bind(f'<Command-{key}>', command)

        try:
            super().start()
        finally:
            self.state.blackout()

    @cached_property
    def lamps(self):
        lamps = {}
        for lamp in self.state.lamps.values():
            lamps.setdefault(lamp.instrument.name, lamp)
        return dict(sorted(lamps.items()))

    def layout(self):
        return [[layout_tabgroup(self.lamps.values())]]

    def set_channel_strip(self, iname, channel, value, *skip):
        instrument = instruments()[iname]
        if isinstance(channel, int):
            channel = instrument.channels[channel]
        _, value = instrument.remap(channel, value)
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
        self.update_instrument(iname)

    def update_instrument(self, iname, levels):
        for k, v in levels.items():
            self.set_channel_strip(iname, k, v)
