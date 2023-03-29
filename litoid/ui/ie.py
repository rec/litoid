from . import ui
from ..state import instruments
from functools import cache
import PySimpleGUI as sg
import datacls

SLIDER = {
    'range': (0, 255),
    'orientation': 'h',
    'expand_x': True,
    'enable_events': True,
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


def _column(instrument, i):
    name = instrument.name
    header = [
        sg.T(instrument.name, s=(8, 1), **TEXT),
        sg.T('<no preset>', k=f'{name}.preset', s=(16, 1), **TEXT),
        sg.T('offset = 000', k=f'{name}.offset', **TEXT),
    ]

    label_size = max(len(c) for c in instrument.channels), 1

    def strip(n, ch):
        name = sg.Text(ch, s=label_size, **TEXT)
        kwargs = {'k':  f'{name}.channel.{ch}', 's': SIZE}

        if names := instrument.value_names.get(ch):
            value = sg.Combo(list(names), **COMBO, **kwargs)
        else:
            value = sg.Slider(**SLIDER, **kwargs)
        return name, value

    body = [strip(n, ch) for n, ch in enumerate(instrument.channels)]
    return [sg.Column([header] + body, k=f'{name}.column', visible=not i)]


@cache
def columns():
    return {k: _column(v, i) for i, (k, v) in enumerate(instruments().items())}


@datacls
class InstrumentEditorApp(ui.UI):
    def layout(self):
        return list(columns().values())


app = InstrumentEditorApp()
LAYOUT = [
    [sg.Text('Some text on Row 1')],
    [sg.Text('Enter something on Row 2'), sg.InputText()],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

if __name__ == "__main__":
    app.start()
