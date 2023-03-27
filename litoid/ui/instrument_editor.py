App = object


class InstrumentEditorApp(App):
    """Instrument mode"""
    BINDINGS = [
        # ("d", "toggle_dark", "Toggle dark mode")
    ]


app = InstrumentEditorApp()

if __name__ == "__main__":
    app.run()
