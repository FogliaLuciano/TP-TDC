import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

plt.ion()


class ControladorVelocidad:
    def __init__(self):
        # Setpoint de 60 km/h en voltios (6 V)
        self.setpoint_volt = 6.0
        self.volt_to_kmh = 10  # Conversión de voltios a km/h (6 V → 60 km/h)

        # Velocidad inicial
        self.velocidad_en_km_h = 0
        self.velocidad_en_volts = self.velocidad_en_km_h / self.volt_to_kmh

        # Tiempo de cada ciclo de scan en segundos
        self.tiempo_scan = 1

        # Parámetros del controlador PID
        self.Kp = 1.5  # Proporcional
        self.Ki = 0.05  # Integral
        self.Kd = 0.1  # Derivativo

        # Variables para el cálculo del PID
        self.integral = 0.0
        self.error_prev = 0.0
        self.control_signal = 0.0

        # Listas para almacenar datos para graficar
        self.tiempos = []
        self.velocidades = []
        self.control_signals = []
        self.errores = []

        # Configuración de los gráficos
        self.fig, self.axs = plt.subplots(3, 1, figsize=(14, 10))
        plt.subplots_adjust(bottom=0.3)

        # Botones para perturbar la velocidad
        self.ax_btn_up = plt.axes([0.3, 0.15, 0.1, 0.05])
        self.btn_up = Button(self.ax_btn_up, "Perturbar -")
        self.btn_up.on_clicked(self.perturbar_arriba)

        self.ax_btn_down = plt.axes([0.6, 0.15, 0.1, 0.05])
        self.btn_down = Button(self.ax_btn_down, "Perturbar +")
        self.btn_down.on_clicked(self.perturbar_abajo)

    def controlador_pid(self, setpoint, realimentacion):
        # Cálculo del error
        error = setpoint - realimentacion

        # Acumulación del error para el término integral
        self.integral += error * self.tiempo_scan

        # Cálculo de la derivada del error
        derivative = (error - self.error_prev) / self.tiempo_scan

        # Cálculo de la señal de control
        self.control_signal = (
            self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        )

        # Actualización del error previo
        self.error_prev = error

        return self.control_signal, error

    def perturbar_arriba(self, event):
        perturbacion = 0.5  # Incremento en voltios (5 km/h)
        self.velocidad_en_volts += perturbacion
        print(f"Perturbación manual: -{perturbacion * self.volt_to_kmh} km/h")

    def perturbar_abajo(self, event):
        perturbacion = -0.5  # Decremento en voltios (-5 km/h)
        self.velocidad_en_volts += perturbacion
        self.velocidad_en_volts = max(0, self.velocidad_en_volts)
        print(f"Perturbación manual: +{abs(perturbacion) * self.volt_to_kmh} km/h")

    def leer_velocimetro(self, velocidad_en_km_h):
        return velocidad_en_km_h / self.volt_to_kmh

    def run(self):
        t = 0
        while True:
            t += self.tiempo_scan

            # Lectura del velocímetro
            realimentacion = self.velocidad_en_volts

            # Controlador PID
            self.control_signal, error = self.controlador_pid(
                self.setpoint_volt, realimentacion
            )

            # Aplicación de la señal de control al variador de frecuencia
            frecuencia_ajuste = self.control_signal  # Simplificación para la simulación

            # Dinámica del vehículo
            self.velocidad_en_km_h += (
                frecuencia_ajuste - 0.05 * self.velocidad_en_km_h
            ) * self.tiempo_scan
            self.velocidad_en_km_h = max(0, self.velocidad_en_km_h)

            # Lectura actualizada del velocímetro
            self.velocidad_en_volts = self.leer_velocimetro(self.velocidad_en_km_h)

            # Registro de datos
            print(
                f"Tiempo: {t} s, Velocidad: {self.velocidad_en_km_h:.2f} km/h, Control: {self.control_signal:.4f}, Error: {error:.4f}"
            )
            self.tiempos.append(t)
            self.velocidades.append(self.velocidad_en_km_h)
            self.control_signals.append(self.control_signal)
            self.errores.append(error)

            # Actualización de los gráficos
            self.actualizar_graficos()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        plt.ioff()
        plt.show()

    def actualizar_graficos(self):
        # Gráfico de velocidad vs tiempo
        self.axs[0].cla()
        self.axs[0].plot(
            self.tiempos, self.velocidades, label="Velocidad (km/h)", color="b"
        )
        self.axs[0].axhline(
            y=self.setpoint_volt * self.volt_to_kmh,
            color="k",
            linestyle="dashed",
            label="Setpoint",
        )
        self.axs[0].set_title("Velocidad del Vehículo")
        self.axs[0].set_xlabel("Tiempo (s)")
        self.axs[0].set_ylabel("Velocidad (km/h)")
        self.axs[0].legend(loc="upper right")
        self.axs[0].grid(True)

        # Gráfico de señal de control vs tiempo
        self.axs[1].cla()
        self.axs[1].plot(
            self.tiempos, self.control_signals, label="Señal de Control", color="g"
        )
        self.axs[1].set_title("Señal de Control")
        self.axs[1].set_xlabel("Tiempo (s)")
        self.axs[1].set_ylabel("Control (V)")
        self.axs[1].legend(loc="upper right")
        self.axs[1].grid(True)

        # Gráfico de error vs tiempo
        self.axs[2].cla()
        self.axs[2].plot(self.tiempos, self.errores, label="Error", color="m")
        self.axs[2].set_title("Error de Control")
        self.axs[2].set_xlabel("Tiempo (s)")
        self.axs[2].set_ylabel("Error (V)")
        self.axs[2].legend(loc="upper right")
        self.axs[2].grid(True)


if __name__ == "__main__":
    controlador = ControladorVelocidad()
    controlador.run()
