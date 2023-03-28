from . import ui
import PySimpleGUI as sg


def T(key, *a, **ka):
    return sg.Text(key, key=key, *a, **ka)


def B(key, *a, **ka):
    return sg.Button(key, key=key, *a, **ka)


HEADER = T('preset_name'), T('instrument_name'), T('offset')
NAMED_CHANNEL = []

LAYOUT = [
    [sg.Text('Some text on Row 1')],
    [sg.Text('Enter something on Row 2'), sg.InputText()],
    [sg.Button('Ok'), sg.Button('Cancel')]
]


class InstrumentEditorApp(ui.UI):
    def layout(self):
        return LAYOUT


app = InstrumentEditorApp()

if __name__ == "__main__":
    app.start()
