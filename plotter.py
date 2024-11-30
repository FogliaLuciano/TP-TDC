import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from modifiers import speed_modifier, acceleration_modifier

fig, ax = plt.subplots()
(line1,) = ax.plot([], [], label="Velocidad")
(line2,) = ax.plot([], [], label="Aceleración")
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_xlabel("Tiempo")
ax.set_ylabel("Magnitudes")
ax.set_title("Variables over Time")
ax.legend()


xdata, ydata1, ydata2 = [], [], []


def update(frame):
    xdata.append(frame)
    ydata1.append(speed_modifier(frame))
    ydata2.append(acceleration_modifier(frame))
    line1.set_data(xdata, ydata1)
    line2.set_data(xdata, ydata2)
    return line1, line2


ani = animation.FuncAnimation(fig, update, frames=np.linspace(0, 100, 1000), blit=True)

plt.show()
