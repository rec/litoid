from ..util.play import play_error
import pyperclip
import json


class Action:
    def __init__(self, ie, msg):
        self.ie = ie
        self.msg = msg

    def __call__(self):
        if self.msg.is_close:
            return

        if self.msg.key.startswith('+'):
            print(self.msg.key)
            return

        el = self.msg.key.split('.')[-1]
        if self.ie.has_focus or el in ('combo', 'focus'):
            getattr(self, el, self._unknown)()

    @property
    def _address(self):
        return self.msg.key.rpartition('.')[0]

    @property
    def _channel(self):
        return self._address.rpartition('.')[-1]

    @property
    def _value(self):
        return self.msg.values.get(self.msg.key)

    def _unknown(self):
        print('unknown', self.msg.key)
        play_error()

    def blackout(self):
        self.ie.blackout()

    def copy(self):
        pyperclip.copy(json.dumps(self.ie.lamp.state))

    def cut(self):
        self.copy()
        play_error()

    def combo(self):
        self.ie.set_ui(self._channel, self._value)

    def focus(self):
        self.ie.has_focus = self._address == 'has'

    def input(self):
        try:
            value = int(self._value)
        except Exception:
            value = 0
        self.ie.set_ui(self._channel, value)

    def new(self):
        play_error()

    def paste(self):
        text = pyperclip.paste()
        try:
            state = json.loads(text)
        except Exception:
            error = 'Cannot parse cut buffer'
        if self.ie.set_state(state):
            error = ''
        else:
            error = 'Failed to set state'
        if error:
            print(error)
            play_error()

    def preset(self):
        self.ie.set_preset(self._value)

    def redo(self):
        play_error()

    def revert(self):
        play_error()

    def save(self):
        play_error()

    def slider(self):
        self.ie.set_ui(self._channel, int(self._value))

    def tabgroup(self):
        name = self.msg.values['tabgroup'].split('.')[0]
        self.ie.lamp = self.ie.lamps[name]

    def undo(self):
        play_error()
