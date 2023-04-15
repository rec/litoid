from .state import State, make_state


class Scene:
    def load(self, state: State) -> bool:
        pass

    def callback(self, state: State, msg: object) -> bool:
        pass

    def unload(self, state: State) -> bool:
        pass

    def run(self, state: State | None = None) -> None:
        state = state or make_state()
        state.scene = self
        state.run()


class PrintScene:
    def load(self, state: State) -> bool:
        print('load', self)

    def callback(self, state: State, msg: object) -> bool:
        print('callback', self, msg)

    def unload(self, state: State) -> bool:
        print('unload', self)
