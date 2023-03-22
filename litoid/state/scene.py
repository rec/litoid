from . state import State
from threading import Lock
import datacls


class Scene:
    def load(self, state: State) -> bool:
        pass

    def callback(self, state: State, msg: object) -> bool:
        pass

    def unload(self, state: State) -> bool:
        pass


@datacls
class Compose(Scene):
    scenes: list[Scene] = datacls.field(list)
    reverse_cb: bool = False

    def load(self, state: State) -> bool:
        return any(s.load(state) for s in self.scenes)

    def callback(self, state: State, msg: object) -> bool:
        scenes = reversed(self.scenes) if self.reverse_cb else self.scenes
        return any(s.callback(state, msg) for s in scenes)

    def unload(self, state: State) -> bool:
        return any(s.unload(state) for s in reversed(self.scenes))


@datacls.mutable
class SceneHolder:
    state: State
    _scene: Scene = datacls.field(Scene)
    _lock: Lock = datacls.field(Lock)

    @property
    def scene(self) -> Scene:
        return self._scene

    @scene.setter
    def set_scene(self, scene: Scene):
        with self._lock:
            self._scene.unload(self.state)
            self._scene = scene
            self._scene.load(self.state)

    def callback(self, msg: object):
        self._scene.callback(self.state, msg)
