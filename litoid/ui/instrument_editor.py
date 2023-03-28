from ..util.is_running import IsRunning
from . import ui
from functools import cached_property
from typing import Callable
import PySimpleGUI as sg
import datacls

sg.theme('DarkAmber')
sg.set_options(font=('Helvetica', 18))

LAYOUT = [
    [sg.Text('Some text on Row 1')],
    [sg.Text('Enter something on Row 2'), sg.InputText()],
    [sg.Button('Ok'), sg.Button('Cancel')]
]


class InstrumentEditorApp(ui.UI):
    pass


app = InstrumentEditorApp(layout=LAYOUT)

if __name__ == "__main__":
    app.start()
