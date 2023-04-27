from . defaults import COMMANDS
from functools import partial
import PySimpleGUI as sg
import xmod

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
BUTTON = {
   'border_width': 1,
   'expand_x': not True,
}
TEXT = {
   'relief': 'raised',
   'border_width': 1,
   'expand_x': not True,
   'justification': 'center',
}
Text = partial(sg.Text, **TEXT)
SLIDER_SIZE = 32, 30
CANVAS_SIZE = 400, 200

_LEN = max(len(c) for c in COMMANDS.values())
CMDS = tuple(f'{v:{_LEN}} (⌘{k.upper()})' for k, v in COMMANDS.items())


def tab(lamp):
    instrument = lamp.instrument
    iname = lamp.iname
    label_size = max(len(c) for c in instrument.channels), 1
    presets = sorted(instrument.presets)

    header = [
        Text(iname, s=(8, 1)),
        sg.Combo(presets, k=f'preset.{iname}', s=(16, 1), **COMBO),
        Text(f'offset = {lamp.offset:03}'),
        sg.ButtonMenu('Menu', ['Commands', CMDS], k=f'menu.{iname}'),
        sg.Button('Blackout', **BUTTON, k=f'blackout.{iname}'),
    ]

    def strip(ch):
        k = f'.{iname}.{ch}'
        label = Text(ch, s=label_size)

        num = sg.Input('0', s=(3, 1), k='input' + k, enable_events=True)
        if n := list(instrument.value_names.get(ch, [])):
            value = sg.Combo(
                n, default_value=n[0], s=SLIDER_SIZE, k='combo' + k, **COMBO
            )
        else:
            value = sg.Slider(**SLIDER, s=SLIDER_SIZE, k='slider' + k)
        return label, num, value

    strips = (strip(ch) for ch in instrument.channels)
    canvas = [sg.Canvas(key=f'canvas.{iname}', s=CANVAS_SIZE)]
    layout = [header, *strips, canvas]

    return sg.Tab(iname, layout, k=f'tab.{iname}')


@xmod
def layout(lamps):
    tabs = [tab(lamp) for lamp in lamps]
    return sg.TabGroup([tabs], enable_events=True, k='tabgroup')
