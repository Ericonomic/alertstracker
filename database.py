from pymongo import MongoClient
from datetime import datetime
import config

# Conectar a MongoDB
client = MongoClient(config.MONGO_URI)
db = client['alertas_db']
coleccion_alertas = db['alertas']
coleccion_rendimientos = db['rendimientos']

def almacenar_alerta(nombre_alerta, contrato_token, precio_inicial):
    alerta = {
        'timestamp': datetime.now(),
        'nombre_alerta': nombre_alerta,
        'token': contrato_token,
        'contrato_token': contrato_token,
        'precio_inicial': precio_inicial,
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
    coleccion_rendimientos.update_one(
        {'nombre_alerta': nombre_alerta},
        {'$set': rendimientos},
        upsert=True
    )

def obtener_alertas(nombre_alerta):
    return list(coleccion_alertas.find({'nombre_alerta': nombre_alerta}))