from . defaults import SIZE, C, T, BUTTON, SLIDER, COMMANDS
import PySimpleGUI as sg
import xmod

_LEN = max(len(c) for c in COMMANDS.values())
CMDS = tuple(f'{v:{_LEN}} (⌘{k.upper()})' for k, v in COMMANDS.items())


@xmod
def lamp_page(lamp):
    instrument = lamp.instrument
    name = instrument.name
    label_size = max(len(c) for c in instrument.channels), 1
    presets = sorted(instrument.presets)

    header = [
        T(name, s=(8, 1)),
        C(presets, k=f'{name}.preset', s=(16, 1)),
        T(f'offset = {lamp.offset:03}'),
        sg.ButtonMenu('Menu', ['Commands', CMDS], k='menu'),
        sg.Button('Blackout', **BUTTON, k=f'{name}.blackout'),
    ]

    def strip(ch):
        k = f'{name}.{ch}.'
        label = T(ch, s=label_size)

        num = sg.Input('0', s=(3, 1), k=k + 'input', enable_events=True)
        if names := instrument.value_names.get(ch):
            value = C(list(names), s=SIZE, k=k + 'combo')
        else:
            value = sg.Slider(**SLIDER, s=SIZE, k=k + 'slider')
        return label, num, value

    strips = (strip(ch) for ch in instrument.channels)
    return [header, *strips]
