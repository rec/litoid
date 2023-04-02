class Action:
    def __init__(self, ie, msg):
        self.ie = ie
        self.msg = msg

    def __call__(self):
        if self.msg.is_close:
            return

        _, _, el = self.msg.key.rpartition('.')
        getattr(self, el, 'unknown')()

    @property
    def _address(self):
        return self.msg.key.rpartition('.')[0]

    @property
    def _channel(self):
        return self._address.rpartition('.')[-1]

    @property
    def _value(self):
        return self.msg.values.get(self.msg.key)

    def unknown(self):
        print('unknown', self.msg.value)

    def tabgroup(self):
        name = self.msg.values['tabgroup'].split('.')[0]
        self.ie.lamp = self.ie.lamps[name]

    def blackout(self):
        self.ie.blackout()

    def preset(self):
        self.ie.set_preset(self._value)

    def menu(self):
        print('menu:', self._value)

    def slider(self):
        self.ie.set_ui(self._channel, int(self._value))

    def combo(self):
        self.ie.set_ui(self._channel, self._value)

    def input(self):
        try:
            value = int(self._value)
        except Exception:
            value = 0
        self.ie.set_ui(self._channel, value)
