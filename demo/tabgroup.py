import PySimpleGUI as sg

sg.theme('DarkAmber')  # Add a touch of color
sg.set_options(font=('Helvetica', 18))


# All the stuff inside your window.
page1 = [
    [sg.Text('Page 1', k='text-1')],
]
tab1 = sg.Tab('tab1', page1, k='tab-1')

# All the stuff inside your window.
page2 = [[sg.Text('Page TWO')], [sg.Button('Ok'), sg.Button('Cancel')]]

tab2 = sg.Tab('tab', page2, k='tab-2')

tabgroup = sg.TabGroup([[tab1, tab2]], enable_events=True, k='tabgroup')
layout = [[tabgroup]]

# Create the Window
window = sg.Window('Window Title', layout, finalize=True)
window.bind('<FocusIn>', '<FocusIn>')
window.bind('<FocusOut>', '<FocusOut>')


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # ifr clicks cancel
        break
    print('You entered ', event, values)

window.close()
