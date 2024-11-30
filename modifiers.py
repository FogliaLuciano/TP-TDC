def speed_modifier(t):
    return 0.5 * t


def acceleration_modifier(t):
    return 3


def punto_suma(setpoint, realimentacion):
    return setpoint - realimentacion


def procesamiento_unidad_control_de_la_consola(error):
    return 0.5 * error


def procesamiento_unidad_correccion_de_la_consola(senial_u):
    return senial_u * 2


def aplicar_variacion_toque(torque_motor, variacion_torque_requerida):
    torque_motor += variacion_torque_requerida
    return torque_motor


def procesamiento_motor(torque_motor):
    return torque_motor


def lectura_velocimetro(senial_salida):
    return senial_salida
