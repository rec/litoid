from pynput.keyboard import Events
from ..state.scene import Scene

KEYS = 'rgbefv'


class RGBKeyboard(Scene):
    def callback(self, state, msg):
        if not isinstance(msg, Events.Press):
            return

        try:
            i = KEYS.index(getattr(msg.key, 'char', None))
        except Exception:
            return
        inc, li = divmod(i, 3)
        inc = 1 - (2 * inc)
        state.dmx.frame[li] = max(0, min(255, state.dmx.frame[li] + inc))
        print(KEYS[li], *state.dmx.frame[0:3])


if __name__ == '__main__':
    RGBKeyboard().run()
