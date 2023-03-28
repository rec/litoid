from . import ui
import PySimpleGUI as sg

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
