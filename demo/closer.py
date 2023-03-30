import PySimpleGUI as sg

layout = [[sg.Text('Command-Q problem')], [sg.Button('Exit')]]
window = sg.Window('Title', layout, enable_close_attempted_event=True)

try:
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Exit':
            print('successful close')
            break
finally:
    print('shutdown code here')

window.close()
