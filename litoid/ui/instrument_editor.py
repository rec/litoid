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



@datacls
class UIDesc:
    theme: str = 'DarkAmber'
    font: tuple[str, int] = ('Helvetica', 18)
    layout: list = datacls.field(list)
    title: str = '💡 Litoid 💡'


@datacls
class UI(UIDesc, IsRunning):
    callback: Callable | None = None

    @cached_property
    def window(self):
        return sg.Window(self.title, self.layout)

    def start(self):
        print('start')
        sg.theme(self.theme)
        sg.set_options(font=self.font)
        super().start()

        while self.running:
            print('reading')
            event, values = window.read()
            print('read', event)
            if event == sg.WIN_CLOSED or event == 'Cancel':
                print('stop!!!')
                self.stop()
                assert not self.running
            self.callback and self.callback((event, values))


if False:
    U = ui.UI
else:
    U = UI


class InstrumentEditorApp(U):
    pass


app = InstrumentEditorApp(layout=LAYOUT)

if __name__ == "__main__":
    app.start()
