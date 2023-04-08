from . defaults import SIZE, T, BUTTON, SLIDER, COMMANDS, COMBO
import PySimpleGUI as sg
import xmod

_LEN = max(len(c) for c in COMMANDS.values())
CMDS = tuple(f'{v:{_LEN}} (⌘{k.upper()})' for k, v in COMMANDS.items())


def tab(lamp):
    instrument = lamp.instrument
    iname = lamp.iname
    label_size = max(len(c) for c in instrument.channels), 1
    presets = sorted(instrument.presets)

    header = [
        T(iname, s=(8, 1)),
        sg.Combo(presets, k=f'preset.{iname}', s=(16, 1), **COMBO),
        T(f'offset = {lamp.offset:03}'),
        sg.ButtonMenu('Menu', ['Commands', CMDS], k=f'menu.{iname}'),
        sg.Button('Blackout', **BUTTON, k=f'blackout.{iname}'),
    ]

    def strip(ch):
        k = f'.{iname}.{ch}'
        label = T(ch, s=label_size)

        num = sg.Input('0', s=(3, 1), k='input' + k, enable_events=True)
        if n := list(instrument.value_names.get(ch, [])):
            value = sg.Combo(n, default_value=n[0], s=SIZE, k='combo' + k)
        else:
            value = sg.Slider(**SLIDER, s=SIZE, k='slider' + k)
        return label, num, value

    strips = (strip(ch) for ch in instrument.channels)
    layout = [header, *strips]
    return sg.Tab(iname, layout, k=f'tab.{iname}')


@xmod
def layout_tabgroup(lamps):
    tabs = [tab(lamp) for lamp in lamps]
    return sg.TabGroup([tabs], enable_events=True, k='tabgroup')
