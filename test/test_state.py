from litoid.state import state
import time


def test_state():
    st = state()
    st.start()
    time.sleep(0.1)
