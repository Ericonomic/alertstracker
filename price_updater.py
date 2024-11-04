import requests
from database import actualizar_precio, actualizar_rendimiento, obtener_alertas

def obtener_precio_token(contrato_token):
    url = f'https://api.dexscreener.com/latest/dex/tokens/{contrato_token}'
    response = requests.get(url)
    data = response.json()

    try:
        return float(data['pairs'][0]['priceUsd'])
    except (KeyError, IndexError):
        return None

def calcular_rendimiento(alertas, campo_inicial, campo_final):
    rendimientos = []
    for alerta in alertas:
        precio_inicial = alerta.get(campo_inicial)
        precio_final = alerta.get(campo_final)
        if precio_inicial and precio_final:
            rendimiento = ((precio_final - precio_inicial) / precio_inicial) * 100
            rendimientos.append(rendimiento)
    return sum(rendimientos) / len(rendimientos) if rendimientos else None

def recalcular_rendimientos():
    nombres_alerta = obtener_alertas(nombre_alerta)
    for nombre in nombres_alerta:
        alertas = obtener_alertas(nombre)
        rendimientos = {
            'nombre_alerta': nombre,
            'rendimiento_1h': calcular_rendimiento(alertas, 'precio_inicial', 'precio_1h'),
            'rendimiento_6h': calcular_rendimiento(alertas, 'precio_inicial', 'precio_6h'),
            'rendimiento_12h': calcular_rendimiento(alertas, 'precio_inicial', 'precio_12h'),
            'rendimiento_24h': calcular_rendimiento(alertas, 'precio_inicial', 'precio_24h'),
            'rendimiento_72h': calcular_rendimiento(alertas, 'precio_inicial', 'precio_72h'),
        }
        actualizar_rendimiento(nombre, rendimientos)