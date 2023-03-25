from pynput.keyboard import Events
from ..state.scene import Scene


class RGBKeyboard(Scene):
    KEYS = '1234567890-=qwertyuiop[]'

    def callback(self, state, msg):
        if not isinstance(msg, Events.Press):
            return
        try:
            i = self.KEYS.index(getattr(msg.key, 'char', None))
        except Exception:
            return
        inc, li = divmod(i, (len(self.KEYS) // 2))
        inc = 1 - (2 * inc)

        lamp = state.lamps['gantom']
        lamp[li] = lamp[li] + inc
        state.dmx.render()


if __name__ == '__main__':
    RGBKeyboard().run()
