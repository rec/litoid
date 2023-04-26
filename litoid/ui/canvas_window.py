from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

CANVAS_KEY = 'data.canvas'


def add_data(window, *plottables):
    if not plottables:
        dataSize = 1000
        xData = np.random.randint(100, size=dataSize)
        yData = np.linspace(0, dataSize, num=dataSize, dtype=int)
        xData.sort(), yData.sort()
        plottables = xData, yData, '.k'

    figure = plt.figure()
    plt.plot(*plottables)

    canvas = window[CANVAS_KEY].TKCanvas
    agg = FigureCanvasTkAgg(figure, canvas)
    agg.draw()
    agg.get_tk_widget().pack(side='top', fill='both', expand=1)
