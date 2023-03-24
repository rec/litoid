from ..state import scene, state
import datacls


@datacls
class Compose(scene.Scene):
    scenes: list[scene.Scene] = datacls.field(list)
    reverse_cb: bool = False

    def load(self, state: state.State) -> bool:
        return any(s.load(state) for s in self.scenes)

    def callback(self, state: state.State, msg: object) -> bool:
        scenes = reversed(self.scenes) if self.reverse_cb else self.scenes
        return any(s.callback(state, msg) for s in scenes)

    def unload(self, state: state.State) -> bool:
        return any(s.unload(state) for s in reversed(self.scenes))
