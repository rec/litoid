from . import defaults, lamp_page, ui
from ..io import hotkey
from ..state import instruments, state as _state
from functools import cached_property
from typing import Callable
import PySimpleGUI as sg
import datacls


@datacls.mutable
class View(ui.UI):
    state: _state.State = datacls.field(_state)
    commands: dict[str, str] = datacls.field(lambda: dict(defaults.COMMANDS))
    callback: Callable = print

    def start(self):
        self.state.blackout()
        self.state.midi_input.start()
        self.hotkeys.start()

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

    @cached_property
    def hotkeys(self):
        return hotkey.HotKeys(self.commands, self.callback)

    def set_window(self, key, value):
        if not isinstance(key, str):
            key = '.'.join(str(k) for k in key)
        self.window[key].update(value=value)

    def layout(self):
        def tab(lamp):
            return sg.Tab(lamp.name, lamp_page(lamp), k=f'{lamp.name}.tab')

        tabs = [tab(lamp) for lamp in self.lamps.values()]
        return [[sg.TabGroup([tabs], enable_events=True, k='tabgroup')]]

    def set_channel_strip(self, iname, channel, value):
        instrument = instruments()[iname]
        if isinstance(channel, int):
            channel = instrument.channels[channel]
        _, value = instrument.remap(channel, value)
        vname = instrument.level_to_name(channel, value)

        self.set_window((iname, channel, 'input'), value)
        if vname:
            self.set_window((iname, channel, 'combo'), vname)
        else:
            self.set_window((iname, channel, 'slider'), value)

    def set_channel_strips(self, iname, levels):
        for k, v in levels.items():
            self.set_channel_strip(iname, k, v)
