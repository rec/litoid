from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np

CANVAS_KEY = 'data.canvas'


def add_data(window, *plottables):
    if not plottables:
        dataSize = 1000
        xData = np.random.randint(100, size=dataSize)
        yData = np.linspace(0, dataSize, num=dataSize, dtype=int)
        plottables = xData, yData

    figure = plt.figure()
    plt.plot(*plottables)

    canvas = window[CANVAS_KEY].TKCanvas
    agg = FigureCanvasTkAgg(figure, canvas)
    agg.draw()
    agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def layout():
    return [[sg.Canvas(key=CANVAS_KEY)]]


def make_window(ui, title='Matplotlib', *plottables):
    window = ui.make_window(title, layout())
    add_data(window)
    return window
