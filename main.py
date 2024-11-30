import numpy as np
import matplotlib.pyplot as plt
import time

# Configuración interactiva para gráficos en tiempo real
plt.ion()

# Parámetros iniciales
setpoint_volt = 5.0  # Setpoint en voltios (proporcional a la velocidad deseada)
volt_to_kmh = 12  # Conversión de voltios a km/h (5 V → 60 km/h)
setpoint_speed = setpoint_volt * volt_to_kmh  # Velocidad deseada (km/h)

# Tiempo de simulación
tiempo_scan = 1  # Intervalo de muestreo en segundos

# Parámetros del PID
Ki = 0.1  # Ganancia integral
Kd = 0.05  # Ganancia derivativa

# Umbrales para la parte proporcional
umbrales_proporcionales = [
    (0, 2, 0.5),
    (2, 5, 1.0),
    (5, 10, 1.5),
    (10, float("inf"), 2.0),
]

# Umbrales para el gráfico
umbrales = {
    "Umbral 3": 55,
    "Umbral 2": 50,
    "Umbral 1": 45,
    "Setpoint": setpoint_speed,
}
color_umbrales = {
    "Umbral 3": "r",
    "Umbral 2": "y",
    "Umbral 1": "g",
    "Setpoint": "b",
}

# Variables de estado
velocidad = 0.0  # Velocidad inicial del motor (km/h)
integral = 0.0  # Integral del error
error_prev = 0.0  # Error previo
control_signal = 0.0  # Señal de control

# Perturbaciones (tiempo relativo: cambio en velocidad)
perturbaciones = {
    10: -5,
    30: 10,
    50: -15,
}

# Listas para graficar
tiempos = []
velocidades = []
control_signals = []
errores = []

# Configuración inicial del gráfico
fig, axs = plt.subplots(3, 1, figsize=(14, 10))


# Función para obtener Kp según los umbrales
def obtener_kp_por_umbrales(error, umbrales):
    abs_error = abs(error)
    for lower, upper, kp in umbrales:
        if lower <= abs_error < upper:
            return kp
    return umbrales[-1][2]


# Función para aplicar perturbaciones
def aplicar_perturbacion(t, velocidad_actual):
    return velocidad_actual + perturbaciones.get(t % 60, 0)


# Función del controlador PID
def controlador_pid(setpoint, realimentacion, integral, error_prev, Ki, Kd, umbrales):
    error = setpoint - realimentacion
    integral += error * tiempo_scan
    derivative = (error - error_prev) / tiempo_scan
    Kp = obtener_kp_por_umbrales(error, umbrales)
    salida_control = Kp * error + Ki * integral + Kd * derivative
    return salida_control, integral, error


# Simulación en tiempo real
t = 0
while (
    t < 300
):  # Para mantenerlo controlado, puedes cambiar el límite o eliminarlo para infinito
    t += tiempo_scan
    # Aplicar perturbaciones
    velocidad = aplicar_perturbacion(t, velocidad)

    # Calcular señal de control
    control_signal, integral, error = controlador_pid(
        setpoint_speed, velocidad, integral, error_prev, Ki, Kd, umbrales_proporcionales
    )
    error_prev = error

    # Variador de frecuencias
    frecuencia_ajuste = 0.1
    velocidad += frecuencia_ajuste * control_signal

    # Limitar velocidad a valores razonables
    velocidad = max(0, velocidad)

    # Actualizar listas
    tiempos.append(t)
    velocidades.append(velocidad)
    control_signals.append(control_signal)
    errores.append(error)

    # Actualizar gráficos
    axs[0].cla()
    axs[0].plot(tiempos, velocidades, label="Velocidad (km/h)", color="b")

    axs[0].axhline(y=60, linestyle="--", label="Setpoint")
    axs[0].axhline(y=65, color="r", linestyle="dashdot", label="Umbral 3")
    axs[0].axhline(y=55, color="r", linestyle="dashdot")
    axs[0].axhline(y=70, color="g", linestyle="dashdot", label="Umbral 2")
    axs[0].axhline(y=50, color="g", linestyle="dashdot")
    axs[0].axhline(y=75, color="b", linestyle="dashdot", label="Umbral 1")
    axs[0].axhline(y=45, color="b", linestyle="dashdot")

    axs[0].set_title("Control PID de Velocidad del Motor (Proporcional con Umbrales)")
    axs[0].set_xlabel("Tiempo (s)")
    axs[0].set_ylabel("Velocidad (km/h)")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].cla()
    axs[1].plot(tiempos, control_signals, label="Señal de Control", color="g")
    axs[1].set_xlabel("Tiempo (s)")
    axs[1].set_ylabel("Control")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].cla()
    axs[2].plot(tiempos, errores, label="Error", color="m")
    axs[2].set_xlabel("Tiempo (s)")
    axs[2].set_ylabel("Error (km/h)")
    axs[2].legend()
    axs[2].grid(True)

    plt.pause(0.01)

    # Simular tiempo real
    time.sleep(tiempo_scan)

plt.ioff()
plt.show()
