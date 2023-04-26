def cli():
    from . import app, litoid

    assert litoid
    app.app(standalone_mode=False)


def gui():
    from .ui.controller import Controller
    import time

    try:
        Controller().start()
    finally:
        time.sleep(0.1)  # Allow daemon threads to print tracebacks


if __name__ == '__main__':
    gui()
