import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

plt.ion()


class ControladorVelocidad:
    def __init__(self):
        self.setpoint_volt = 6.0
        self.volt_to_kmh = 10  # Conversión de voltios a km/h (6 V → 60 km/h)
        self.setpoint_speed = self.setpoint_volt * self.volt_to_kmh

        self.tiempo_scan = 1

        self.Ki = 0.2
        self.Kd = 0.2

        self.umbrales_proporcionales = [
            (0, 1, 1.0),  # Rango de error [0, 1): Kp = 1.0
            (1, 2, 1.5),  # Rango de error [1, 2): Kp = 1.5
            (2, 3, 2.0),  # Rango de error [2, 3): Kp = 2.0
            (3, float("inf"), 3.0),  # Error >= 3: Kp = 3.0
        ]

        self.umbrales_frecuencias = [
            (0, 2, 0.05),  # Rango de error [0, 2): Frecuencia = 0.05
            (2, 5, 0.1),  # Rango de error [2, 5): Frecuencia = 0.1
            (5, 10, 0.2),  # Rango de error [5, 10): Frecuencia = 0.2
            (10, float("inf"), 0.3),  # Error >= 10: Frecuencia = 0.3
        ]

        self.umbrales = {
            "Umbral 1": 1,
            "Umbral 2": 2,
            "Umbral 3": 3,
        }

        self.color_umbrales = {
            "Umbral 1": "r",
            "Umbral 2": "y",
            "Umbral 3": "g",
        }

        self.velocidad = self.setpoint_speed
        self.integral = 0.0
        self.error_prev = 0.0
        self.control_signal = 0.0

        self.tiempos = []
        self.velocidades = []
        self.control_signals = []
        self.errores = []

        self.fig, self.axs = plt.subplots(3, 1, figsize=(14, 10))
        plt.subplots_adjust(bottom=0.3)

        self.ax_btn_up = plt.axes([0.3, 0.15, 0.1, 0.05])
        self.btn_up = Button(self.ax_btn_up, "Perturbar +")
        self.btn_up.on_clicked(self.perturbar_arriba)

        self.ax_btn_down = plt.axes([0.6, 0.15, 0.1, 0.05])
        self.btn_down = Button(self.ax_btn_down, "Perturbar -")
        self.btn_down.on_clicked(self.perturbar_abajo)

    def obtener_valor_por_umbrales(self, error, umbrales):
        abs_error = abs(error)
        for lower, upper, value in umbrales:
            if lower <= abs_error < upper:
                return value
        return umbrales[-1][2]

    def controlador_pid(self, setpoint, realimentacion, integral, error_prev, Ki, Kd):
        error = setpoint - realimentacion

        integral += error * self.tiempo_scan
        derivative = (error - error_prev) / self.tiempo_scan
        Kp = self.obtener_valor_por_umbrales(error, self.umbrales_proporcionales)
        salida_control = Kp * error + Ki * integral + Kd * derivative
        return salida_control, integral, error

    def aplicar_ajuste_frecuencia(self, error):
        frecuencia_ajuste = self.obtener_valor_por_umbrales(
            error, self.umbrales_frecuencias
        )
        return frecuencia_ajuste

    def perturbar_arriba(self, event):
        perturbacion = 2
        self.velocidad += perturbacion
        print(f"Perturbación manual: +{perturbacion} km/h")

    def perturbar_abajo(self, event):
        perturbacion = -2
        self.velocidad += perturbacion
        self.velocidad = max(0, self.velocidad)
        print(f"Perturbación manual: {perturbacion} km/h")

    def run(self, tiempo_total=300):
        t = 0
        while t < tiempo_total:
            t += self.tiempo_scan

            self.control_signal, self.integral, error = self.controlador_pid(
                self.setpoint_speed,
                self.velocidad,
                self.integral,
                self.error_prev,
                self.Ki,
                self.Kd,
            )
            self.error_prev = error

            frecuencia_ajuste = self.aplicar_ajuste_frecuencia(error)

            self.velocidad += frecuencia_ajuste * self.control_signal

            self.velocidad = max(0, self.velocidad)

            print(
                f"Tiempo: {t:.2f} s, Velocidad: {self.velocidad:.2f} km/h, Control: {self.control_signal:.2f}, Error: {error:.2f}"
            )

            self.tiempos.append(t)
            self.velocidades.append(self.velocidad)
            self.control_signals.append(self.control_signal)
            self.errores.append(error)

            self.actualizar_graficos()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            time.sleep(self.tiempo_scan)

        plt.ioff()
        plt.show()

    def actualizar_graficos(self):
        self.axs[0].cla()
        self.axs[0].plot(
            self.tiempos, self.velocidades, label="Velocidad (km/h)", color="b"
        )

        for nombre_umbral, valor_umbral in self.umbrales.items():
            self.axs[0].axhline(
                y=self.setpoint_speed + valor_umbral,
                color=self.color_umbrales[nombre_umbral],
                linestyle="dashdot",
                label=f"{nombre_umbral} +",
            )
            self.axs[0].axhline(
                y=self.setpoint_speed - valor_umbral,
                color=self.color_umbrales[nombre_umbral],
                linestyle="dashdot",
                label=f"{nombre_umbral} -",
            )

        self.axs[0].axhline(
            y=self.setpoint_speed, color="k", linestyle="dotted", label="Setpoint"
        )

        self.axs[0].set_title(
            "Control PID de Velocidad del Motor (Frecuencia y Proporcional por Umbrales)"
        )
        self.axs[0].set_xlabel("Tiempo (s)")
        self.axs[0].set_ylabel("Velocidad (km/h)")
        self.axs[0].legend(loc="upper right")
        self.axs[0].grid(True)

        self.axs[1].cla()
        self.axs[1].plot(
            self.tiempos, self.control_signals, label="Señal de Control", color="g"
        )
        self.axs[1].set_xlabel("Tiempo (s)")
        self.axs[1].set_ylabel("Control")
        self.axs[1].legend()
        self.axs[1].grid(True)

        self.axs[2].cla()
        self.axs[2].plot(self.tiempos, self.errores, label="Error", color="m")
        self.axs[2].set_xlabel("Tiempo (s)")
        self.axs[2].set_ylabel("Error (km/h)")
        self.axs[2].legend()
        self.axs[2].grid(True)


if __name__ == "__main__":
    controlador = ControladorVelocidad()
    controlador.run()
