import schedule
import time
from datetime import datetime
from price_updater import obtener_precio_token, recalcular_rendimientos
from database import actualizar_precio

alertas_programadas = []

def programar_actualizaciones(alerta_id, contrato_token, timestamp):
    alertas_programadas.append({'alerta_id': alerta_id, 'contrato_token': contrato_token, 'timestamp': timestamp})

def verificar_precios_pendientes():
    ahora = datetime.now()
    for alerta in alertas_programadas:
        tiempo_transcurrido = (ahora - alerta['timestamp']).total_seconds()
        alerta_id, contrato_token = alerta['alerta_id'], alerta['contrato_token']

        if tiempo_transcurrido >= 3600 and 'precio_1h' not in alerta:
            actualizar_precio(alerta_id, 'precio_1h', obtener_precio_token(contrato_token))
            alerta['precio_1h'] = True

        if tiempo_transcurrido >= 21600 and 'precio_6h' not in alerta:
            actualizar_precio(alerta_id, 'precio_6h', obtener_precio_token(contrato_token))
            alerta['precio_6h'] = True

        # Repetir para 12h, 24h, y 72h
        # Al final, recalcular rendimientos
    recalcular_rendimientos()

def iniciar_programador():
    schedule.every(10).minutes.do(verificar_precios_pendientes)
    while True:
        schedule.run_pending()
        time.sleep(1)