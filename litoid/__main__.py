def cli():
    from . import app, litoid

    assert litoid
    app.app(standalone_mode=False)


def gui():
    import time

    from .ui.controller import Controller

    try:
        Controller().start()
    finally:
        time.sleep(0.1)  # Allow daemon threads to print tracebacks


if __name__ == '__main__':
    gui()
