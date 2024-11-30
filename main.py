import time
from modifiers import (
    aplicar_variacion_torque,
    lectura_velocimetro,
    procesamiento_motor,
    procesamiento_unidad_correccion_de_la_consola,
    punto_suma,
    procesamiento_unidad_control_de_la_consola,
)
import threading
from perturbaciones import generar_perturbacion
from plotter import Plotter
from global_variables import GlobalVariables

hilos_activos = True


def bucle_infinito():
    global hilos_activos

    torque_motor = 0  # Porque arranca en reposo
    setpoint = 6  # Volts que seran traducidos a km/h

    while hilos_activos:
        GlobalVariables.senial_error = punto_suma(
            setpoint, GlobalVariables.senial_realimentacion
        )
        senial_u = procesamiento_unidad_control_de_la_consola(
            GlobalVariables.senial_error
        )
        variacion_torque_requerida = procesamiento_unidad_correccion_de_la_consola(
            senial_u
        )
        torque_motor = aplicar_variacion_torque(
            torque_motor, variacion_torque_requerida
        )
        senial_salida = procesamiento_motor(torque_motor)
        GlobalVariables.senial_realimentacion = lectura_velocimetro(senial_salida)

        # Descomentar para debuggear
        # print(f"Torque motor: {torque_motor}")
        # print(f"Senial realimentacion: {GlobalVariables.senial_realimentacion}")
        # print(f"Senial error: {GlobalVariables.senial_error}")
        # print(f"Senial u: {senial_u}")
        # print(f"Variacion torque requerida: {variacion_torque_requerida}")
        # print(f"Senial salida: {senial_salida}")
        # print("*****************************************************")

        time.sleep(1)


def bucle_lectura_perturbaciones():
    global hilos_activos
    while hilos_activos:
        entrada = input("Ingrese un tipo de perturbacion: ")
        if entrada == "exit":
            hilos_activos = False
        else:
            print(f"Generando perturbacion de tipo {entrada}")
        generar_perturbacion(entrada)


hilo_bucle = threading.Thread(target=bucle_infinito)
hilo_entrada = threading.Thread(target=bucle_lectura_perturbaciones)

hilo_bucle.start()
hilo_entrada.start()

plotter = Plotter()
plotter.preparar_plot()

hilo_bucle.join()
hilo_entrada.join()
