from . import ui
from ..io import midi
from ..state import scene, state as _state
from functools import partial
import PySimpleGUI as sg
import datacls

SLIDER = {
    'range': (0, 255),
    'orientation': 'h',
    'expand_x': True,
    'enable_events': True,
    'disable_number_display': True,
}
COMBO = {
    'enable_events': True,
    'readonly': True,
}
TEXT = {
   'relief': 'raised',
   'border_width': 1,
   'expand_x': not True,
   'justification': 'center',
}
SIZE = 32, 30
T = partial(sg.T, **TEXT)


def _channel(lamp):
    instrument = lamp.instrument
    name = lamp.name
    label_size = max(len(c) for c in instrument.channels), 1

    def strip(n, ch):
        k = f'{name}.{ch}.'
        label = T(ch, s=label_size)

        num = sg.Input('0', s=(3, 1), k=k + 'input', enable_events=True)
        if names := instrument.value_names.get(ch):
            value = sg.Combo(list(names), **COMBO, s=SIZE, k=k + 'combo')
        else:
            value = sg.Slider(**SLIDER, s=SIZE, k=k + 'slider')
        return label, num, value

    header = [
        T(name, s=(8, 1)),
        T('<no preset>', k=f'{name}.preset', s=(16, 1)),
        T(f'offset = {lamp.offset:03}', k=f'{name}.offset'),
    ]

    body = (strip(n, ch) for n, ch in enumerate(instrument.channels))
    return [header, *body]


@datacls.mutable
class InstrumentEditorApp(ui.UI):
    state: _state.State = datacls.field(_state)

    lamp = None

    @property
    def lamps(self):
        return self.state.lamps

    def callback(self, msg):
        if msg.key == 'tabgroup':
            name = msg.values['tabgroup'].split('.')[0]
            self.lamp = self.lamps[name]
            return

        try:
            new_value = msg.values[msg.key]

        except Exception:
            return

        lamp_name, ch, el = msg.key.split('.')
        lamp = self.lamps[lamp_name]
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
        return sg.Tab(lamp.name, _channel(lamp), k=f'{lamp.name}.tab')

    def layout(self):
        lamps = list(self.lamps.values())
        tabs = [self.tab(lamp) for lamp in lamps]
        self.lamp = lamps[0]

        return [[sg.TabGroup([tabs], enable_events=True, k='tabgroup')]]

    def start(self):
        self.state.set_scene(Scene(self))
        self.state.midi_input.start()
        try:
            super().start()
        finally:
            for lamp in self.state.lamps.values():
                lamp.blackout()

    def set_level(self, ch, v):
        if self.lamp[ch] == v:
            return
        self.lamp[ch] = v
        channel = self.lamp.instrument.channels[ch]
        k = f'{self.lamp.name}.{channel}.'
        self.window[k + 'input'].update(value=v)
        if (name := self.lamp.instrument.level_to_name(ch, v)) is not None:
            self.window[k + 'combo'].update(value=name)
        else:
            self.window[k + 'slider'].update(value=v)


class Scene(scene.Scene):
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
