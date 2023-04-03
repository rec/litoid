from . import action, defaults, lamp_page, ui
from ..io import hotkey, midi
from ..state import instruments, scene, state as _state
from ..util.play import play_error
from functools import cached_property
import PySimpleGUI as sg
import copy
import datacls


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

    def set(self, key, value):
        if not isinstance(key, str):
            key = '.'.join(str(k) for k in key)
        self.window[key].update(value=value)

    def set_ui(self, address, new_value):
        # TODO remove dependency on the current lamp
        iname, ch = address.split('.')
        chan, new_value = self.instrument.remap(ch, new_value)

        try:
            level = max(0, min(255, int(new_value)))
        except (ValueError, TypeError):
            level = 0

        self.lamp[chan] = level

        k = f'{self.lamp.name}.{ch}.'
        self.set(k + 'input', level)
        if name := self.instrument.level_to_name(ch, level):
            self.set(k + 'combo', name)
        else:
            self.set(k + 'slider', level)

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
            self.reset_levels()
            return True
        else:
            play_error(f'Wrong instrument {name}')

    def set_preset(self, name):
        # BROKEN
        if preset := self.all_presets.get(self.iname, {}).get(name):
            for ch in self.instrument.channels:
                self.set_ui(ch, preset[ch])
        else:
            play_error(f'No preset named {name}')

    def blackout(self):
        self.lamp.blackout()
        self.reset_levels()

    def layout(self):
        def tab(lamp):
            return sg.Tab(lamp.name, lamp_page(lamp), k=f'{lamp.name}.tab')

        lamps = list(self.lamps.values())
        tabs = [tab(lamp) for lamp in lamps]
        self.lamp = lamps[0]

        return [[sg.TabGroup([tabs], enable_events=True, k='tabgroup')]]

    def set_level(self, ch, v, scale_name=False):
        if ch < len(self.lamp):
            if scale_name:
                if self.instrument.channels[ch] in self.instrument.value_names:
                    v *= 2
            if self.lamp[ch] == v:
                return
            self.lamp[ch] = v
            self.reset_level(ch)

    def reset_level(self, ch):
        v = self.lamp[ch]
        channel = self.lamp.instrument.channels[ch]
        k = f'{self.lamp.name}.{channel}.'
        self.window[k + 'input'].update(value=v)
        if (name := self.lamp.instrument.level_to_name(ch, v)) is not None:
            self.window[k + 'combo'].update(value=name)
        else:
            self.window[k + 'slider'].update(value=v)

    def reset_levels(self):
        for i in range(len(self.instrument.channels)):
            self.reset_level(i)


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
            self.ie.set_level(channel, value, scale_name=True)


def main():
    try:
        app = InstrumentEditorApp()
        app.start()
    finally:
        import time
        time.sleep(0.1)


if __name__ == "__main__":
    main()
