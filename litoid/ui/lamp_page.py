from . defaults import SIZE, COMBO, T, BUTTON, SLIDER
import PySimpleGUI as sg
import xmod


@xmod
def lamp_page(lamp):
    instrument = lamp.instrument
    name = lamp.name
    label_size = max(len(c) for c in instrument.channels), 1
    presets = sorted(instrument.presets)
    commands = ['Copy', 'Restore', 'Save']

    header = [
        T(name, s=(8, 1)),
        sg.Combo(presets, k=f'{name}.preset', s=(16, 1), **COMBO),
        T(f'offset = {lamp.offset:03}', k=f'{name}.offset'),
        sg.ButtonMenu('Menu', ['', commands], k=f'{name}.menu'),
        sg.Button('Blackout', **BUTTON, k=f'{name}.blackout'),
    ]

    def strip(ch):
        k = f'{name}.{ch}.'
        label = T(ch, s=label_size)

        num = sg.Input('0', s=(3, 1), k=k + 'input', enable_events=True)
        if names := instrument.value_names.get(ch):
            value = sg.Combo(list(names), **COMBO, s=SIZE, k=k + 'combo')
        else:
            value = sg.Slider(**SLIDER, s=SIZE, k=k + 'slider')
        return label, num, value

    strips = (strip(ch) for ch in instrument.channels)
    return [header, *strips]
