import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from global_variables import GlobalVariables


class Plotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        (self.line1,) = self.ax.plot([], [], label="Error")
        (self.line2,) = self.ax.plot([], [], label="Realimentacion")
        self.xdata = []
        self.ydata1 = []
        self.ydata2 = []

    def preparar_plot(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Magnitudes")
        self.ax.set_title("Variables over Time")
        self.ax.legend()
        ani = animation.FuncAnimation(
            self.fig, self._update, frames=np.linspace(0, 100, 1000), blit=True
        )
        plt.show()

    def _update(self, frame):
        senial_error = GlobalVariables.senial_error
        senial_realimentacion = GlobalVariables.senial_realimentacion

        self.xdata.append(frame)
        self.ydata1.append(senial_error)
        self.ydata2.append(senial_realimentacion)
        self.line1.set_data(self.xdata, self.ydata1)
        self.line2.set_data(self.xdata, self.ydata2)
        return self.line1, self.line2
