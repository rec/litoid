from functools import cached_property
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datacls


@datacls
class Canvas:
    window: object
    iname: str

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
