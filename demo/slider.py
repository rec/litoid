import PySimpleGUI as sg
layout = [
   [sg.Text(
       'Hello World',
       enable_events=True,
       key='-TEXT-',
       font=('Arial Bold', 20),
       size=(50, 2),
       relief="raised",
       border_width=5,
       expand_x=True,
       justification='center',
    )],

   [sg.Slider(
       range=(10, 30),
       default_value=12,
       expand_x=True,
       enable_events=True,
       orientation='horizontal',
       key='-SL-'
       )]
]
window = sg.Window('Hello', layout, size=(715, 150))
while True:
   event, values = window.read()
   print(event, values)
   if event == sg.WIN_CLOSED or event == 'Exit':
      break
   if event == '-SL-':
      window['-TEXT-'].update(font=('Arial Bold', int(values['-SL-'])))
window.close()
