import time

from litoid.state import state


def test_state():
    st = state()
    st.start()
    time.sleep(0.1)
