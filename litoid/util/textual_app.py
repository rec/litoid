from textual import app, widgets
import threading
import time

__all__ = 'App', 'app', 'widgets'


class App(app.App):
    def run(self, *a, **ka):
        def light():
            # Hacky fix for dark mode
            time.sleep(0.001)
            self.call_from_thread(setattr, self, 'dark', False)

        threading.Thread(target=light).start()
        super().run(*a, **ka)
