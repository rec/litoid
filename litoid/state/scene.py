from .state import State


class Scene:
    def load(self, state: State) -> bool:
        pass

    def callback(self, state: State, msg: object) -> bool:
        pass

    def unload(self, state: State) -> bool:
        pass


class PrintScene(Scene):
    def load(self, state: State) -> bool:
        print('load', self)

    def callback(self, state: State, msg: object) -> bool:
        print('callback', self, msg)

    def unload(self, state: State) -> bool:
        print('unload', self)


class CallbackScene(Scene):
    def __init__(self, callback):
        self._callback = callback

    def callback(self, state: State, msg: object) -> bool:
        self._callback(msg)

    def unload(self, state: State):
        self._callback(None)
