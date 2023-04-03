from . import action, defaults, lamp_page, ui
from ..io import hotkey, midi
from ..state import instruments, scene, state as _state
from ..util.play import play_error
from functools import cached_property
from typing import Callable
import PySimpleGUI as sg
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
        self.view.state.set_scene(MidiScene(self))
        self.view.start()

    def callback(self, msg):
        if isinstance(msg, str):
            name, values = msg, None
        elif msg.key == 'menu':
            name, values = msg.values['menu'], msg.values
        else:
            name = None
        if name is not None:
            name = name.split()[0].strip('.').lower()
            msg = ui.Message(name, values)
        return action.Action(self, msg)()

    def copy(self):
        return {self.iname: self.lamp.levels()}

    def paste(self, levels):
        if value := levels.get(self.iname):
            self.lamp.set_levels(value)
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
        self.set_channel_levels(self.iname, self.lamp.levels())

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


@datacls.mutable
class InstrumentEditorApp(ui.UI):
    state: _state.State = datacls.field(_state)
    commands: dict[str, str] = datacls.field(lambda: dict(defaults.COMMANDS))

    lamp = None

    def start(self):
        self.state.blackout()
        self.state.set_scene(MidiScene(self))
        self.state.midi_input.start()
        self.hotkeys.start()

        try:
            super().start()
        finally:
            for lamp in self.state.lamps.values():
                lamp.blackout()

    @cached_property
    def hotkeys(self):
        return hotkey.HotKeys(self.commands, self.callback)

    @cached_property
    def lamps(self):
        return self.state.lamps

    @cached_property
    def instrument(self):
        return self.lamp.instrument

    @cached_property
    def all_presets(self):
        return {k: copy.deepcopy(v.presets) for k, v in instruments().items()}

    @cached_property
    def current_presets(self):
        return {k: None for k in self.all_presets}

    def set_window(self, key, value):
        if not isinstance(key, str):
            key = '.'.join(str(k) for k in key)
        self.window[key].update(value=value)

    def set_address_value(self, address, new_value):
        # TODO remove dependency on the current lamp
        iname, ch = address.split('.')
        chan, new_value = self.instrument.remap(ch, new_value)

        try:
            level = max(0, min(255, int(new_value)))
        except (ValueError, TypeError):
            level = 0

        self.lamp[chan] = level

        k = f'{self.lamp.name}.{ch}.'
        self.set_window(k + 'input', level)
        if name := self.instrument.level_to_name(ch, level):
            self.set_window(k + 'combo', name)
        else:
            self.set_window(k + 'slider', level)

    def callback(self, msg):
        if isinstance(msg, str):
            name, values = msg, None
        elif msg.key == 'menu':
            name, values = msg.values['menu'], msg.values
        else:
            name = None
        if name is not None:
            name = name.split()[0].strip('.').lower()
            msg = ui.Message(name, values)
        return action.Action(self, msg)()

    def levels(self):
        return {self.lamp.instrument.name: self.lamp.levels()}

    def set_levels(self, levels):
        if value := levels.get(name := self.lamp.instrument.name):
            self.lamp.set_levels(value)
            self.set_channel_strips()
            return True
        else:
            play_error(f'Wrong instrument {name}')

    def set_preset(self, name):
        # BROKEN
        if preset := self.all_presets.get(self.iname, {}).get(name):
            for ch in self.instrument.channels:
                self.set_address_value(ch, preset[ch])
        else:
            play_error(f'No preset named {name}')

    def blackout(self):
        self.lamp.blackout()
        self.set_channel_strips()

    def layout(self):
        def tab(lamp):
            return sg.Tab(lamp.name, lamp_page(lamp), k=f'{lamp.name}.tab')

        lamps = list(self.lamps.values())
        tabs = [tab(lamp) for lamp in lamps]
        self.lamp = lamps[0]

        return [[sg.TabGroup([tabs], enable_events=True, k='tabgroup')]]

    def set_midi_level(self, ch, v, scale_name=False):
        if ch < len(self.lamp):
            if scale_name:
                if self.instrument.channels[ch] in self.instrument.value_names:
                    v *= 2
            if self.lamp[ch] == v:
                return
            self.lamp[ch] = v
            self.set_channel_strip(ch)

    def set_channel_strip(self, ch):
        v = self.lamp[ch]
        channel = self.lamp.instrument.channels[ch]
        k = f'{self.lamp.name}.{channel}.'
        self.window[k + 'input'].update(value=v)
        if (name := self.lamp.instrument.level_to_name(ch, v)) is not None:
            self.window[k + 'combo'].update(value=name)
        else:
            self.window[k + 'slider'].update(value=v)

    def set_channel_strips(self):
        for i in range(len(self.instrument.channels)):
            self.set_channel_strip(i)


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
        if not True:
            app = InstrumentEditorApp()
        else:
            app = Controller.make()
        app.start()
    finally:
        import time
        time.sleep(0.1)


if __name__ == "__main__":
    main()
