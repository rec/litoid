from ..util.textual_app import App
from textual.widgets import Header, Footer


class InstrumentEditorApp(App):
    """Instrument mode"""
    BINDINGS = [
        # ("d", "toggle_dark", "Toggle dark mode")
    ]

    def compose(self):
        yield Header()
        yield Footer()


app = InstrumentEditorApp()

if __name__ == "__main__":
    app.run()
