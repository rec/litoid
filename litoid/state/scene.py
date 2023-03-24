from .state import State
from threading import Lock
import datacls


class Scene:
    def load(self, state: State) -> bool:
        pass

    def callback(self, state: State, msg: object) -> bool:
        pass

    def unload(self, state: State) -> bool:
        pass

    def run(self, state: State | None = None) -> None:
        state = state or State()
        state.set_scene(self)
        state.run()


class PrintScene:
    def load(self, state: State) -> bool:
        print('load', self)

    def callback(self, state: State, msg: object) -> bool:
        print('callback', self, msg)

    def unload(self, state: State) -> bool:
        print('unload', self)


@datacls
class SceneHolder:
    state: State
    _scene: Scene = PrintScene()
    _lock: Lock = datacls.field(Lock)

    @property
    def scene(self) -> Scene:
        return self._scene

    def set_scene(self, scene: Scene):
        with self._lock:
            self._scene.unload(self.state)
            self.__dict__['_scene'] = scene
            self._scene.load(self.state)

    def callback(self, msg: object):
        # should I lock this?
        self._scene.callback(self.state, msg)
