from .. import log
import PySimpleGUI as sg
import pyperclip


class Action:
    def __init__(self, controller, msg):
        self.controller = controller
        self.view = controller.view
        self.model = self.controller.model
        self.msg = msg

    def __call__(self):
        if self.msg.is_close:
            self.view.stop()
        else:
            getattr(self, self.msg.action, self._unknown)()

    @property
    def _value(self):
        return self.msg.values.get(self.msg.key)

    def _set_level(self, v: int | str, *skip):
        self.controller.set_level(self.msg.channel, v, *skip)

    def _unknown(self):
        log.error('Unknown key', self.msg.key)

    def blackout(self):
        self.controller.blackout()

    def combo(self):
        self._set_level(self._value, 'combo')

    def copy(self):
        pyperclip.copy(self.controller.copy())

    def cut(self):
        if self.model.delete_selected():
            self.copy()
            self.view.update_selector()

    def input(self):
        try:
            value = int(self._value)
        except Exception:
            value = 0
        self._set_level(value, 'input')

    def menu(self):
        name = self._value.split()[0].strip('.').lower()
        method = getattr(self, name)
        method()

    def new(self):
        if name := sg.popup_get_text('Enter new preset name').strip():
            self.controller.new(name)

    def paste(self):
        self.controller.paste(pyperclip.paste())

    def preset(self):
        self.controller.set_preset(self._value)

    def request_close(self):
        log.debug('request_close')
        self.model.save_recorders()

        if self.model.is_dirty:
            choice = self.view.yes_no_cancel(
                'Unsaved changes?',
                ['Do you want to save your unsaved changes?'],
            )
            if choice == 'Cancel':
                log.error('Cancelled')
                return
            if choice == 'Yes':
                self.model.save_all()
        self.view.stop()
        log.debug('closed')

    def revert(self):
        ch = sg.popup_ok_cancel(
            f'Revert to saved for {self.controller.iname}?',  title='Revert'
        )
        if ch == 'OK':
            self.model.revert()
        elif ch != 'Cancel':
            log.error(f'Got "{ch}", not OK or Cancel')

    def save(self):
        if self.model.is_instrument_dirty:
            self.model.save()
        else:
            log.error('Nothing to save')

    def slider(self):
        self._set_level(int(self._value), 'slider')

    def tabgroup(self):
        tab, iname = self._value.split('.')
        assert tab == 'tab'
        self.model.iname = iname
