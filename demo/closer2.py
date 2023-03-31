import PySimpleGUI as sg

def mac_quit(window):
    window.write_event_value('Mac Quit', None)

layout = [[sg.Text('Command-Q problem')], [sg.Button('Exit')]]
window = sg.Window('Title', layout, enable_close_attempted_event=True, finalize=True)

"""
tk::mac::Quit
If a proc of this name is defined it is the default Apple Event handler for kAEQuitApplication, “quit”,
the Apple Event sent when your application is asked to be quit,
e.g. via the quit menu item in the application menu, the quit menu item in the Dock menu,
or during a logout/restart/shutdown etc. If this is not defined, exit is called instead.
"""

sg.Window.hidden_master_root.createcommand("tk::mac::Quit" , lambda win=window:mac_quit(win))

while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Exit':
        print('closed')
        break
    elif event == 'Mac Quit':
        print('Mac Quit')
        break

window.close()
