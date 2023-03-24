from litoid.state.state import State
import time


def test_state():
    state = State()
    state.start()
    time.sleep(0.1)
