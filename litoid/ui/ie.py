from . import ui
from ..state import instruments
from functools import cache
import PySimpleGUI as sg
import datacls

SLIDER = {
    'range': (0, 255),
    'orientation': 'h',
}
COMBO = {
    'enable_events': True,
    'readonly': True,
}


def _column(instrument, i):
    name = instrument.name
    header = [
        sg.T(instrument.name),
        sg.T('<no preset>', k=f'{name}.preset'),
        sg.T('offset=0', k=f'{name}.offset'),
    ]

    def strip(n, ch):
        name = sg.T(ch)
        key = f'{name}.channel.{ch}'

        if names := instrument.value_names.get(ch):
            value = sg.Combo(list(names), **COMBO, k=key)
        else:
            value = sg.Slider(**SLIDER, k=key)
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
