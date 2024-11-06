from pymongo import MongoClient
from datetime import datetime
import config

# Configuración de la conexión con MongoDB desactivando la verificación de certificados
client = MongoClient(
    config.MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client['alertas_db']
coleccion_alertas = db['alertas']
coleccion_rendimientos = db['rendimientos']

def almacenar_alerta(nombre_alerta, contrato_token, precio_inicial):
    # Verificar si la alerta ya existe para evitar duplicados
    alerta_existente = coleccion_alertas.find_one({
        'nombre_alerta': nombre_alerta,
        'contrato_token': contrato_token
    })
    
    if alerta_existente:
        return alerta_existente['_id']  # Si ya existe, devolver su ID en lugar de crear una nueva

    # Insertar una nueva alerta si no existe
    alerta = {
        'timestamp': datetime.now(),
        'nombre_alerta': nombre_alerta,
        'contrato_token': contrato_token,
        'precio_inicial': precio_inicial,
        'precio_1m': None,
        'precio_5m': None,
        'precio_1h': None,
        'precio_6h': None,
        'precio_12h': None,
        'precio_24h': None,
        'precio_72h': None
    }
    return coleccion_alertas.insert_one(alerta).inserted_id

def actualizar_precio(alerta_id, campo_precio, precio):
    coleccion_alertas.update_one(
        {'_id': alerta_id},
        {'$set': {campo_precio: precio}}
    )

def actualizar_rendimiento(nombre_alerta, rendimientos):
    # Actualizar el rendimiento y el conteo en la colección 'rendimientos'
    update_data = {'$set': rendimientos}
    
    # Incrementar el conteo de alertas para cada campo
    for campo in rendimientos:
        if campo.startswith('precio_'):
            contador_campo = f'n_calculo_alertas_{campo.split("_")[1]}'
            update_data['$inc'] = {contador_campo: 1}

    coleccion_rendimientos.update_one(
        {'nombre_alerta': nombre_alerta},
        update_data,
        upsert=True
    )

def obtener_alertas(nombre_alerta):
    return list(coleccion_alertas.find({'nombre_alerta': nombre_alerta}))
