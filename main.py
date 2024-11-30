import time
from modifiers import (
    aplicar_variacion_toque,
    lectura_velocimetro,
    procesamiento_motor,
    procesamiento_unidad_correccion_de_la_consola,
    punto_suma,
    procesamiento_unidad_control_de_la_consola,
)

# 1 volt = 10 km/h ?
# 5v --> 50km/h ?
# 10v --> 100km/h ?


# Valores iniciales
torque_motor = 0  # Porque arranca en reposo
setpoint = 6  # Volts que seran traducidos a km/h
senial_realimentacion = 0

# Bucle infinito para simular las iteraciones
while True:
    senial_error = punto_suma(setpoint, senial_realimentacion)
    senial_u = procesamiento_unidad_control_de_la_consola(senial_error)
    variacion_torque_requerida = procesamiento_unidad_correccion_de_la_consola(senial_u)
    torque_motor = aplicar_variacion_toque(torque_motor, variacion_torque_requerida)
    senial_salida = procesamiento_motor(torque_motor)
    senial_realimentacion = lectura_velocimetro(senial_salida)

    # Graficar las seniales con el plotter
    print(f"Torque motor: {torque_motor}")
    print(f"Senial realimentacion: {senial_realimentacion}")
    print(f"Senial error: {senial_error}")
    print(f"Senial u: {senial_u}")
    print(f"Variacion torque requerida: {variacion_torque_requerida}")
    print(f"Senial salida: {senial_salida}")
    print(f"Senial realimentacion: {senial_realimentacion}")
    print("*****************************************************")
    time.sleep(1)
