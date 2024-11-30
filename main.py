import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

# Configuración interactiva para gráficos en tiempo real
plt.ion()


class ControladorVelocidad:
    def __init__(self):
        # Parámetros iniciales
        self.setpoint_volt = (
            6.0  # Setpoint en voltios (proporcional a la velocidad deseada)
        )
        self.volt_to_kmh = 10  # Conversión de voltios a km/h (6 V → 60 km/h)
        self.setpoint_speed = (
            self.setpoint_volt * self.volt_to_kmh
        )  # Velocidad deseada en km/h

        # Intervalo de muestreo en segundos
        self.tiempo_scan = 1

        # Parámetros del PID (Ajustados)
        self.Ki = 0.2
        self.Kd = 0.2

        # Umbrales para la parte proporcional (Ajustados)
        self.umbrales_proporcionales = [
            (0, 1, 1.0),  # Rango de error [0, 1): Kp = 1.0
            (1, 2, 1.5),  # Rango de error [1, 2): Kp = 1.5
            (2, 3, 2.0),  # Rango de error [2, 3): Kp = 2.0
            (3, float("inf"), 3.0),  # Error >= 3: Kp = 3.0
        ]

        # Umbrales para las frecuencias del variador (Originales)
        self.umbrales_frecuencias = [
            (0, 2, 0.05),  # Rango de error [0, 2): Frecuencia = 0.05
            (2, 5, 0.1),  # Rango de error [2, 5): Frecuencia = 0.1
            (5, 10, 0.2),  # Rango de error [5, 10): Frecuencia = 0.2
            (10, float("inf"), 0.3),  # Error >= 10: Frecuencia = 0.3
        ]

        # Umbrales para el gráfico
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

        # Variables de estado
        self.velocidad = self.setpoint_speed
        self.integral = 0.0
        self.error_prev = 0.0
        self.control_signal = 0.0

        # Listas para graficar
        self.tiempos = []
        self.velocidades = []
        self.control_signals = []
        self.errores = []

        # Configuración inicial del gráfico
        self.fig, self.axs = plt.subplots(3, 1, figsize=(14, 10))
        plt.subplots_adjust(bottom=0.3)  # Ajuste para acomodar botones

        # Configuración de botones
        # Botón para perturbar hacia arriba
        self.ax_btn_up = plt.axes(
            [0.3, 0.15, 0.1, 0.05]
        )  # [left, bottom, width, height]
        self.btn_up = Button(self.ax_btn_up, "Perturbar +")
        self.btn_up.on_clicked(self.perturbar_arriba)

        # Botón para perturbar hacia abajo
        self.ax_btn_down = plt.axes(
            [0.6, 0.15, 0.1, 0.05]
        )  # [left, bottom, width, height]
        self.btn_down = Button(self.ax_btn_down, "Perturbar -")
        self.btn_down.on_clicked(self.perturbar_abajo)

    # Función para obtener un valor por umbrales
    def obtener_valor_por_umbrales(self, error, umbrales):
        abs_error = abs(error)
        for lower, upper, value in umbrales:
            if lower <= abs_error < upper:
                return value
        return umbrales[-1][2]

    # Función del controlador PID
    def controlador_pid(self, setpoint, realimentacion, integral, error_prev, Ki, Kd):
        error = setpoint - realimentacion

        # Unidad de control PID
        integral += error * self.tiempo_scan
        derivative = (error - error_prev) / self.tiempo_scan
        Kp = self.obtener_valor_por_umbrales(error, self.umbrales_proporcionales)
        salida_control = Kp * error + Ki * integral + Kd * derivative
        return salida_control, integral, error

    # Función para aplicar ajuste de frecuencia
    def aplicar_ajuste_frecuencia(self, error):
        frecuencia_ajuste = self.obtener_valor_por_umbrales(
            error, self.umbrales_frecuencias
        )
        return frecuencia_ajuste

    # Métodos para los botones de perturbación
    def perturbar_arriba(self, event):
        perturbacion = 2  # Puedes ajustar el valor de perturbación
        self.velocidad += perturbacion
        print(f"Perturbación manual: +{perturbacion} km/h")

    def perturbar_abajo(self, event):
        perturbacion = -2  # Puedes ajustar el valor de perturbación
        self.velocidad += perturbacion
        self.velocidad = max(0, self.velocidad)  # Evitar velocidad negativa
        print(f"Perturbación manual: {perturbacion} km/h")

    # Método principal de simulación
    def run(self, tiempo_total=300):
        t = 0
        while t < tiempo_total:
            t += self.tiempo_scan

            # Calcular señal de control
            self.control_signal, self.integral, error = self.controlador_pid(
                self.setpoint_speed,
                self.velocidad,
                self.integral,
                self.error_prev,
                self.Ki,
                self.Kd,
            )
            self.error_prev = error

            # Obtener frecuencia ajustada según el error
            frecuencia_ajuste = self.aplicar_ajuste_frecuencia(error)

            # Aplicar el ajuste de frecuencia
            self.velocidad += frecuencia_ajuste * self.control_signal

            # Limitar velocidad a valores razonables
            self.velocidad = max(0, self.velocidad)

            print(
                f"Tiempo: {t:.2f} s, Velocidad: {self.velocidad:.2f} km/h, Control: {self.control_signal:.2f}, Error: {error:.2f}"
            )

            # Actualizar listas
            self.tiempos.append(t)
            self.velocidades.append(self.velocidad)
            self.control_signals.append(self.control_signal)
            self.errores.append(error)

            # Actualizar gráficos
            self.actualizar_graficos()

            # Actualizar la figura
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            time.sleep(self.tiempo_scan)

        plt.ioff()
        plt.show()

    # Método para actualizar los gráficos
    def actualizar_graficos(self):
        # Gráfico de Velocidad
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

        # Gráfico de Señal de Control
        self.axs[1].cla()
        self.axs[1].plot(
            self.tiempos, self.control_signals, label="Señal de Control", color="g"
        )
        self.axs[1].set_xlabel("Tiempo (s)")
        self.axs[1].set_ylabel("Control")
        self.axs[1].legend()
        self.axs[1].grid(True)

        # Gráfico de Error
        self.axs[2].cla()
        self.axs[2].plot(self.tiempos, self.errores, label="Error", color="m")
        self.axs[2].set_xlabel("Tiempo (s)")
        self.axs[2].set_ylabel("Error (km/h)")
        self.axs[2].legend()
        self.axs[2].grid(True)


# Crear una instancia del controlador y ejecutar la simulación
if __name__ == "__main__":
    controlador = ControladorVelocidad()
    controlador.run()
