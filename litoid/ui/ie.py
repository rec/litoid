from . import ui
from ..state import state as _state
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


@datacls
class InstrumentEditorApp(ui.UI):
    state: _state.State = datacls.field(_state)

    @property
    def lamps(self):
        return self.state.lamps

    def callback(self, msg):
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
        lamps = self.lamps.values()
        tabs = [self.tab(lamp) for lamp in lamps]
        return [[sg.TabGroup([tabs])]]

    def start(self):
        try:
            super().start()
        finally:
            for lamp in self.state.lamps.values():
                lamp.blackout()


def main():
    app = InstrumentEditorApp()
    app.start()
    import time
    time.sleep(0.5)


if __name__ == "__main__":
    main()
