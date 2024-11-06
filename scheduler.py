import time
import threading
from datetime import datetime, timedelta
from price_updater import obtener_precio_token
from database import actualizar_precio, coleccion_alertas, actualizar_rendimiento
import logging

logger = logging.getLogger(__name__)

def programar_actualizaciones(alerta_id, contrato_token, timestamp_inicial):
    # Programar actualizaciones para 1 minuto, 5 minutos, 1 hora, 6 horas, 12 horas, 24 horas y 72 horas
    intervalos = {
        'precio_1m': timedelta(minutes=1),
        'precio_5m': timedelta(minutes=5),
        'precio_1h': timedelta(hours=1),
        'precio_6h': timedelta(hours=6),
        'precio_12h': timedelta(hours=12),
        'precio_24h': timedelta(hours=24),
        'precio_72h': timedelta(hours=72)
    }

    for campo_precio, intervalo in intervalos.items():
        tiempo_actualizacion = timestamp_inicial + intervalo
        threading.Thread(target=programar_actualizacion_individual, args=(alerta_id, contrato_token, campo_precio, tiempo_actualizacion)).start()

def programar_actualizacion_individual(alerta_id, contrato_token, campo_precio, tiempo_actualizacion):
    # Esperar hasta el tiempo de actualización
    tiempo_espera = (tiempo_actualizacion - datetime.now()).total_seconds()
    if tiempo_espera > 0:
        time.sleep(tiempo_espera)

    # Obtener el precio y actualizar la base de datos
    precio = obtener_precio_token(contrato_token)
    if precio is not None:
        actualizar_precio(alerta_id, campo_precio, precio)
        logger.info(f'Precio actualizado para {campo_precio}: {precio} para alerta ID {alerta_id}')
        calcular_y_registrar_rendimiento(alerta_id, campo_precio, precio)
    else:
        logger.warning(f"No se pudo obtener el precio para {campo_precio} en la alerta ID {alerta_id}")

def calcular_y_registrar_rendimiento(alerta_id, campo_precio, precio_actual):
    # Obtener el precio inicial y calcular el rendimiento
    alerta = coleccion_alertas.find_one({'_id': alerta_id})
    if not alerta or 'precio_inicial' not in alerta:
        logger.warning(f"No se pudo calcular el rendimiento: Precio inicial no encontrado para alerta ID {alerta_id}")
        return

    precio_inicial = alerta['precio_inicial']
    rendimiento = round(((precio_actual - precio_inicial) / precio_inicial) * 100, 2)  # Rendimiento en porcentaje con 2 decimales
    logger.info(f'Rendimiento calculado para {campo_precio} en alerta ID {alerta_id}: {rendimiento:.2f}%')

    # Actualizar en la colección de rendimientos con el rendimiento y el conteo
    actualizar_rendimiento(alerta['nombre_alerta'], {campo_precio: rendimiento})
