import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

plt.ion()


class ControladorVelocidad:
    def __init__(self):
        self.setpoint_volt = 6.0
        self.volt_to_kmh = 10  # Conversión de voltios a km/h (6 V → 60 km/h)

        # Velocidad inicial
        self.velocidad_en_km_h = 0
        self.velocidad_en_volts = self.velocidad_en_km_h / self.volt_to_kmh

        self.tiempo_scan = 1

        self.Kp = 1.5
        self.Ki = 0.05
        self.Kd = 0.1

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

    def controlador_pid(self, setpoint, realimentacion):
        # INICIO PUNTO SUMA
        error = setpoint - realimentacion
        # FIN PUNTO SUMA

        # INICIO UNIDAD DE CONTROL DE LA CONSOLA
        self.integral += error * self.tiempo_scan

        derivative = (error - self.error_prev) / self.tiempo_scan

        self.control_signal = (
            self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        )

        self.error_prev = error

        return self.control_signal, error
        # FIN UNIDAD DE CONTROL DE LA CONSOLA

    def perturbar_arriba(self, event):
        perturbacion_kmh = 30  # Perturbación de 30 km/h
        self.velocidad_en_km_h += perturbacion_kmh
        self.velocidad_en_volts = self.leer_velocimetro(self.velocidad_en_km_h)
        print(f"Perturbación manual: +{perturbacion_kmh} km/h")

    def perturbar_abajo(self, event):
        perturbacion_kmh = 30  # Perturbación de 30 km/h
        self.velocidad_en_km_h = max(0, self.velocidad_en_km_h - perturbacion_kmh)
        self.velocidad_en_volts = self.leer_velocimetro(self.velocidad_en_km_h)
        print(f"Perturbación manual: -{perturbacion_kmh} km/h")

    def leer_velocimetro(self, velocidad_en_km_h):
        return velocidad_en_km_h / self.volt_to_kmh

    def run(self):
        t = 0
        while True:
            t += self.tiempo_scan

            # INICIO PUNTO SUMA Y UNIDAD DE CONTROL DE LA CONSOLA (PLC)
            realimentacion = self.velocidad_en_volts
            self.control_signal, error = self.controlador_pid(
                self.setpoint_volt, realimentacion
            )
            # FIN PUNTO SUMA Y UNIDAD DE CONTROL DE LA CONSOLA

            # INICIO UNIDAD DE CORRECCION DE LA CONSOLA (VARIADOR DE FRECUENCIAS)
            frecuencia_ajuste = self.control_signal - 0.05 * self.velocidad_en_km_h
            # FIN UNIDAD DE CORRECCION DE LA CONSOLA

            # INICO PLANTA/PROCESO (MOTOR)
            self.velocidad_en_km_h += frecuencia_ajuste * self.tiempo_scan
            self.velocidad_en_km_h = max(0, self.velocidad_en_km_h)
            # FIN PLANTA/PROCESO

            # INICIO VELOCIMETRO
            self.velocidad_en_volts = self.leer_velocimetro(self.velocidad_en_km_h)
            # FIN VELOCIMETRO

            print(
                f"Tiempo: {t} s, Velocidad: {self.velocidad_en_km_h:.2f} km/h, Control: {self.control_signal:.4f}, Error: {error:.4f}"
            )
            self.tiempos.append(t)
            self.velocidades.append(self.velocidad_en_km_h)
            self.control_signals.append(self.control_signal)
            self.errores.append(error)

            self.actualizar_graficos()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        plt.ioff()
        plt.show()

    def actualizar_graficos(self):
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

        self.axs[1].cla()
        self.axs[1].plot(
            self.tiempos, self.control_signals, label="Señal de Control", color="g"
        )
        self.axs[1].set_title("Señal de Control")
        self.axs[1].set_xlabel("Tiempo (s)")
        self.axs[1].set_ylabel("Control (V)")
        self.axs[1].legend(loc="upper right")
        self.axs[1].grid(True)

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
