from functools import cached_property
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datacls


@datacls
class DrawingCanvas:
    window: object
    lamp: object

    @cached_property
    def iname(self) -> str:
        return self.lamp.instrument.name

    @cached_property
    def key(self) -> str:
        return f'canvas.{self.iname}'

    @cached_property
    def canvas(self):
        return self.window[self.key].TKCanvas

    @cached_property
    def figure(self):
        return plt.figure(self.key)

    @cached_property
    def tk_agg(self):
        return FigureCanvasTkAgg(self.figure, self.canvas)

    def draw(self, *a, **ka):
        if a or ka:
            plt.plot(*a, figure=self.figure, **ka)

        self.tk_agg.draw()
        self.tk_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    def draw_recorder(self, recorder):
        channels = (str(c) for c in self.lamp.channel_range)
        tracks = (t for c in channels if (t := recorder.tracks.get(c)))
        data = (i for t in tracks for i in t.astuple())

        self.draw(*data)
