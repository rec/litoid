from .state import State, state as _state
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
        state = state or _state()
        state.scene = self
        state.run()


class PrintScene:
    def load(self, state: State) -> bool:
        print('load', self)

    def callback(self, state: State, msg: object) -> bool:
        print('callback', self, msg)

    def unload(self, state: State) -> bool:
        print('unload', self)


@datacls.mutable
class SceneHolder:
    state: State
    _scene: Scene | None = None
    _lock: Lock = datacls.field(Lock)

    @property
    def scene(self) -> Scene:
        return self._scene

    @scene.setter
    def scene(self, scene: Scene):
        with self._lock:
            if self._scene:
                self._scene.unload(self.state)
            self.__dict__['_scene'] = scene
            if self._scene:
                self._scene.load(self.state)

    def callback(self, msg: object):
        with self._lock:
            scene = self._scene
        if scene:
            # should I lock this?
            scene.callback(self.state, msg)
