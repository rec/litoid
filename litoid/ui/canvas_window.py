import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def draw_figure(window, figure, canvas):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def make_figure(window, canvas_key):
    dataSize = 1000
    xData = np.random.randint(100, size=dataSize)
    yData = np.linspace(0, dataSize, num=dataSize, dtype=int)

    figure = plt.figure()

    plt.plot(xData, yData, '.k')
    canvas = window[canvas_key].TKCanvas
    draw_figure(window, figure, canvas)


def make_window(ui, title='Matplotlib', canvas_key='test.canvas'):
    layout = [[sg.Canvas(key=canvas_key)]]
    window = ui.make_window(title, layout)
    make_figure(window, canvas_key)
