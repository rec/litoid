from ..util.play import play_error
import PySimpleGUI as sg
import pyperclip
import json


class Action:
    def __init__(self, controller, msg):
        self.controller = controller
        self.view = controller.view
        self.model = self.controller.model
        self.msg = msg

    def __call__(self):
        if self.msg.is_close:
            return

        if self.msg.key.startswith('+'):
            print(self.msg.key)
            return
        getattr(self, self.msg.action, self._unknown)()

    @property
    def _value(self):
        return self.msg.values.get(self.msg.key)

    def _set_channel_level(self, value):
        self.controller.set_channel_level(
            self.msg.name, self.msg.channel, value
        )

    def _unknown(self):
        print('unknown', self.msg.key)
        play_error()

    def blackout(self):
        self.controller.blackout()

    def copy(self):
        pyperclip.copy(json.dumps(self.controller.copy()))

    def cut(self):
        self.copy()
        play_error()

    def combo(self):
        self._set_channel_level(self._value)

    def input(self):
        try:
            value = int(self._value)
        except Exception:
            value = 0
        self._set_channel_level(value)

    def menu(self):
        name = self._value.split()[0].strip('.').lower()
        method = getattr(self, name)
        method()

    def new(self):
        name = sg.popup_get_text('Enter new patch name')
        print(name)

    def paste(self):
        text = pyperclip.paste()
        try:
            state = json.loads(text)
        except Exception:
            play_error('Bad JSON in cut buffer\n\n', text)
            raise
        else:
            if not self.controller.paste(state):
                play_error('Failed to set state')

    def preset(self):
        # BROKEN
        self.view.set_preset(self._value)

    def redo(self):
        play_error()

    def revert(self):
        play_error()

    def save(self):
        play_error()

    def slider(self):
        self._set_channel_level(int(self._value))

    def tabgroup(self):
        name = self._value.split('.')[0]
        self.model.current_instrument = name
        self.view.window.refresh()

    def undo(self):
        play_error()
