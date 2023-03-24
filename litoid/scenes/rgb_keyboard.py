from pynput.keyboard import Events
from ..state.scene import Scene


class RGBKeyboardOld(Scene):
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
        state.dmx.frame[li] = max(0, min(255, state.dmx.frame[li] + inc))
        state.dmx.render()
        print(self.KEYS[li], *state.dmx.frame[0:len(self.KEYS)])


class RGBKeyboard(RGBKeyboardOld):
    KEYS = 'qwertyuasdfghj'


if __name__ == '__main__':
    RGBKeyboard().run()
