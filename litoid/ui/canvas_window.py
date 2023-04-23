import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def draw_figure(window, figure):
    canvas = window['test.canvas'].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def make_figure(window):
    dataSize = 1000
    xData = np.random.randint(100, size=dataSize)
    yData = np.linspace(0, dataSize, num=dataSize, dtype=int)

    figure = plt.figure()
    plt.plot(xData, yData, '.k')
    draw_figure(window, figure)


def make_window(ui):
    layout = [[sg.Canvas(key='test.canvas')]]
    window = ui.make_window('Matplotlib', layout)
    make_figure(window)
