import PySimpleGUI as sg
from functools import partial

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
T = partial(sg.T, **TEXT)
SIZE = 32, 30


def C(items, *a, **ka):
    if items:
        ka.setdefault('default_value', items[0])
    return sg.Combo(items, *a, **ka, **COMBO)
