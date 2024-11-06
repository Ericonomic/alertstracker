import requests
import logging

logger = logging.getLogger(__name__)

def obtener_precio_token(contrato_token):
    try:
        # Llamada a la API de Dexscreener para obtener el precio del token
        url = f'https://api.dexscreener.com/latest/dex/tokens/{contrato_token}'
        response = requests.get(url)
        response.raise_for_status()  # Genera una excepción si la respuesta HTTP es un error

        data = response.json()

        # Verificar que la estructura de los datos es la esperada
        if 'pairs' in data and data['pairs']:
            # Intentar extraer el precio en USD
            precio_usd = data['pairs'][0].get('priceUsd')
            if precio_usd is not None:
                return float(precio_usd)
            else:
                logger.warning(f"El precio en USD no se encontró para el token {contrato_token}.")
                return None
        else:
            logger.warning(f"Estructura de datos inesperada para el token {contrato_token}: {data}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error de red al obtener el precio para el token {contrato_token}: {e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Error al procesar los datos de la API para el token {contrato_token}: {e}")
        return None

def recalcular_rendimientos():
    # Implementación de recalcular_rendimientos
    logger.info("Recalculando rendimientos...")
    # Aquí va la lógica de recalcular rendimientos