from . import lamp_page, ui
from ..io import midi
from ..state import scene, state as _state
from functools import cached_property
import PySimpleGUI as sg
import datacls


@datacls.mutable
class InstrumentEditorApp(ui.UI):
    state: _state.State = datacls.field(_state)

    lamp = None

    @property
    def lamps(self):
        return self.state.lamps

    @property
    def instrument(self):
        return self.lamp.instrument

    def callback(self, msg):
        if not True:
            return Callback(ie=self, **msg.asdict())()
        if msg.key == 'tabgroup':
            name = msg.values['tabgroup'].split('.')[0]
            self.lamp = self.lamps[name]
            return

        if msg.key.endswith('blackout'):
            self.lamp.blackout()
            self.reset_levels()
            return

        try:
            new_value = msg.values[msg.key]

        except Exception:
            return

        lamp_name, ch, el = msg.key.split('.')
        lamp = self.lamps[lamp_name]
        assert lamp == self.lamp

        instrument = lamp.instrument
        ch_names = instrument.value_names.get(ch)

        def set_value(key, value):
            k = f'{lamp_name}.{ch}.{key}'
            msg.values[k] = value
            self.window[k].update(value=value)

        if el == 'slider':
            set_value('input', level := int(new_value))

        elif el == 'combo':
            set_value('input', level := ch_names[new_value])

        elif el == 'input':
            try:
                level = max(0, min(255, int(new_value)))
            except (ValueError, TypeError):
                level = 0

            set_value('input', level)
            if ch_names:
                set_value('combo', instrument.level_to_name(ch, level))
            else:
                set_value('slider', level)

        ch, level = instrument.remap(ch, level)
        lamp[ch] = level

    def tab(self, lamp):
        return sg.Tab(lamp.name, lamp_page(lamp), k=f'{lamp.name}.tab')

    def layout(self):
        lamps = list(self.lamps.values())
        tabs = [self.tab(lamp) for lamp in lamps]
        self.lamp = lamps[0]

        return [[sg.TabGroup([tabs], enable_events=True, k='tabgroup')]]

    def start(self):
        self.state.blackout()
        self.state.set_scene(MidiScene(self))
        self.state.midi_input.start()
        try:
            super().start()
        finally:
            for lamp in self.state.lamps.values():
                lamp.blackout()

    def set_level(self, ch, v):
        if ch < len(self.lamp):
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
        for i in range(len(self.lamp.instrument.channels)):
            self.reset_level(i)


@datacls
class Callback(ui.Message):
    ie: InstrumentEditorApp

    def __call__(self):
        getattr(self, '_' + self.command, self._error)()

    def __getattr__(self, k):
        if k.startswith('_'):
            raise AttributeError(k)
        return getattr(self.ie, k)

    @cached_property
    def channel(self):
        lamp_name, channel, comp = self.key.split('.')
        assert lamp_name == self.lamp.name
        assert self.comp == comp
        return channel

    @cached_property
    def command(self):
        return self.key.partition('.')[-1]

    @cached_property
    def value(self):
        return self.values.get(self.key)

    def _error(self):
        print('Do not understand message', self.msg.key)

    def _tabgroup(self):
        name = self.values['tabgroup'].split('.')[0]
        self.ie.lamp = self.lamps[name]

    def _blackout(self):
        self.lamp.blackout()
        self.reset_levels()

    def _slider(self):
        self.set_input(int(self.value))

    def _combo(self):
        self.set_input(self.instrument.full_value_names[self.value])

    def _input(self):
        try:
            level = max(0, min(255, int(self.value)))
        except (ValueError, TypeError):
            level = 0

        self.set_input(level)
        if name := self.instrument.level_to_name(self.channel, level):
            self.set_value('combo', name)
        else:
            self.set_value('slider', level)

    def set_input(self, value):
        self.set_value('input', value)
        self.lamp[self.channel] = value

    def set_value(self, key, value):
        k = f'{self.lamp.name}.{self.channnel}.{key}'
        self.window[k].update(value=value)


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
            self.ie.set_level(channel, value)


def main():
    app = InstrumentEditorApp()
    app.start()


if __name__ == "__main__":
    main()
