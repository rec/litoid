if __name__ == '__main__':
    from . import app, litoid

    assert litoid
    app.app(standalone_mode=False)
