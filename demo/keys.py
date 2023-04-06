import PySimpleGUI as sg
from functools import partial

layout = [
    [sg.Button("ok", size=(10, 2), key='button1'),
     sg.Button("exit", size=(10, 2), key='button2')],
]
window = sg.Window('Hotkeys', layout, use_default_focus=False, finalize=True)
button1, button2 = window['button1'], window['button2']
USE_TK = not True

window.TKroot

keys = '<alt>+<f>', '<ctrl>+<f>', '<cmd>+<f>', '<Left>', '<Right>'
keys = '<Alt_L>+<f>', '<Control_L>+<f>', '<Left>', '<Right>'
keys = '<Command-f>', '<Control-f>', '<Shift-f>'

if not False:
    for k in keys:
        if USE_TK:
            window.TKroot.bind(k, partial(print, k))
        else:
            window.bind(k, 'tk ' + k)
else:
    def key_cb(event):
        print(str(event))
        print(event.char, event.state, type(event.state))


    window.TKroot.bind('<Key>', key_cb)

button1.Widget.configure(underline=0, takefocus=0)
button2.Widget.configure(underline=1, takefocus=0)

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED:
        break
    elif event in ("button1", "ALT-o"):
        print('OK')
    elif event in ("button2", "ALT-x"):
        break

window.close()
