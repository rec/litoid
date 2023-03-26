from ..util.textual_app import App
from textual.widgets import Header, Footer


class InstrumentEditorApp(App):
    """Instrument mode"""
    BINDINGS = [
        # ("d", "toggle_dark", "Toggle dark mode")
    ]

    def run(self, *a, **ka):
        import threading
        import time

        def light():
            # Hacky fix for dark mode
            time.sleep(0.001)
            self.call_from_thread(setattr, self, 'dark', False)

        threading.Thread(target=light).start()
        super().run(*a, **ka)

    def compose(self):
        yield Header()
        yield Footer()


app = InstrumentEditorApp()

if __name__ == "__main__":
    app.run()
