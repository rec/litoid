from . dmx import DMX
from . midi import MidiInput
from . timed_heap import TimedHeap
from functools import cached_property
from threading import Lock
import datacls


@datacls
class State:
    dmx_port: str = '/dev/cu.usbserial-6AYL2V8Z'
    midi_input_name: str | None = None

    @cached_property
    def dmx(self):
        return DMX(self.dmx_port)

    @cached_property
    def midi_input(self):
        return MidiInput(self.scene.midi_callback, self.midi_input_name)

    @cached_property
    def timed_heap(self):
        return TimedHeap()

    @cached_property
    def scene(self):
        return SceneHolder(self)


class Scene:
    def load(self, state: State):
        pass

    def midi_callback(self, state: State, msg):
        pass

    def unload(self, state: State):
        pass


@datacls
class Compose(Scene):
    scenes: list[Scene] = datacls.field(list)
    reverse_midi: bool = False

    def load(self, state: State):
        return any(s.load(state) for s in self.scenes)

    def midi_callback(self, state: State, msg):
        scenes = reversed(self.scenes) if self.reverse_midi else self.scenes
        return any(s.midi_callback(state, msg) for s in scenes)

    def unload(self, state: State):
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

    def midi_callback(self, msg):
        self._scene.midi_callback(self.state, msg)
