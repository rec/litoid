import PySimpleGUI as sg

sg.theme('DarkAmber')   # Add a touch of color
sg.set_options(font=('Helvetica', 18))

# All the stuff inside your window.
page1 = [
    [sg.Text('Page 1')],
]

# All the stuff inside your window.
page2 = [
    [sg.Text('Page TWO')],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

tab1 = sg.Tab('tab1', page1, k='+TAB1+')
tab2 = sg.Tab('tab', page2, k='+TAB2+')

tabgroup = sg.TabGroup([[tab1, tab2]], enable_events=True)
layout = [[tabgroup]]

# Create the Window
window = sg.Window('Window Title', layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # ifr clicks cancel
        break
    print('You entered ', values[0])

window.close()
