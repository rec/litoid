from . import ui
from ..state import instruments, lamp
from functools import cache, partial
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


def _column(lamp):
    return [sg.Column(_channel(lamp), k=f'{lamp.name}.column')]


@cache
def columns():
    return {k: _column(v, i) for i, (k, v) in enumerate(instruments().items())}


@datacls
class InstrumentEditorApp(ui.UI):
    lamps: list[lamp.Lamp, ...] = datacls.field(list)

    def callback(self, msg):
        def set_value(key, value):
            msg.values[key] = value
            self.window[key].update(value=value)

        value = msg.values[msg.key]
        print(msg.key, value)
        address, _, el = msg.key.rpartition('.')
        if el == 'slider':
            set_value(f'{address}.input', int(value))
        elif el == 'combo':
            pass

    def layout(self):
        return [_column(lamp) for lamp in self.lamps.values()]


def main():
    from litoid.state import state

    app = InstrumentEditorApp(lamps=state().lamps)
    app.start()


if __name__ == "__main__":
    main()
