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
        for la in self.state.lamps.values():
            lamps.setdefault(la.instrument.name, la)
        return dict(sorted(lamps.items()))

    def set_window(self, key, value):
        if not isinstance(key, str):
            key = '.'.join(str(k) for k in key)
        self.window[key].update(value=value)

    def layout(self):
        return [[layout_tabgroup(self.lamps.values())]]

    def set_channel_strip(self, iname, channel, value):
        instrument = instruments()[iname]
        if isinstance(channel, int):
            channel = instrument.channels[channel]
        _, value = instrument.remap(channel, value)
        vname = instrument.level_to_name(channel, value)

        def set_window(action, value):
            key = f'{action}.{iname}.{channel}'
            self.window[key].update(value=value)

        set_window('input', value)
        if vname:
            set_window('combo', vname)
        else:
            set_window('slider', value)

    def set_channel_strips(self, iname, levels):
        for k, v in levels.items():
            self.set_channel_strip(iname, k, v)
