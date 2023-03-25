from pynput.keyboard import Events
from ..state.scene import Scene


class RGBKeyboardBase(Scene):
    KEYS = 'rgbefv'

    def callback(self, state, msg):
        if not isinstance(msg, Events.Press):
            return
        try:
            i = self.KEYS.index(getattr(msg.key, 'char', None))
        except Exception:
            return
        inc, li = divmod(i, (len(self.KEYS) // 2))
        inc = 1 - (2 * inc)
        self._callback(state, li, inc)

    def _callback(self, state, li, inc):
        state.dmx.frame[li] = max(0, min(255, state.dmx.frame[li] + inc))
        state.dmx.render()
        print(self.KEYS[li], *state.dmx.frame[0:len(self.KEYS)])


class RGBKeyboardMed(RGBKeyboardBase):
    KEYS = 'qwertyuasdfghj'


class RGBKeyboard(RGBKeyboardBase):
    KEYS = '1234567890-=qwertyuiop[]'

    def _callback(self, state, li, inc):
        lamp = state.lamps['gantom']
        lamp[li] = lamp[li] + inc
        state.dmx.render()


if __name__ == '__main__':
    RGBKeyboard().run()
