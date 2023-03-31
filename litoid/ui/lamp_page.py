from . defaults import SIZE, COMBO, T, BUTTON, SLIDER
import PySimpleGUI as sg
import xmod


@xmod
def lamp_page(lamp):
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
        sg.Button('Blackout', **BUTTON, k=f'{name}.blackout'),
    ]

    body = (strip(n, ch) for n, ch in enumerate(instrument.channels))
    return [header, *body]
