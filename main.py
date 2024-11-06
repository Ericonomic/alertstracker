import logging
import threading
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import config
from alert_parser import extraer_nombre_alerta, extraer_contrato_token
from database import almacenar_alerta
from price_updater import obtener_precio_token
from scheduler import programar_actualizaciones
from commands import agregar_manejadores
from datetime import datetime
import time

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Función para manejar mensajes de alerta
async def handle_message(update, context):
    try:
        if not update.message or not update.message.text:
            logger.warning("Mensaje vacío o no válido recibido.")
            return

        message = update.message.text

        # Verificar si el mensaje es del grupo y topic especificados
        if (
            update.message.chat_id == config.GROUP_ID and
            update.message.message_thread_id == config.TOPIC_ID
        ):
            # Registrar el mensaje recibido en el log
            logger.info(f'Mensaje recibido del topic: {message}')

            # Procesar el mensaje si es una alerta
            if "Transactions within" in message:
                try:
                    nombre_alerta = extraer_nombre_alerta(message)
                    if nombre_alerta is None:
                        logger.warning("No se pudo extraer el nombre de la alerta.")
                        return
                    logger.debug(f'Nombre de la alerta extraído: {nombre_alerta}')
                except Exception as e:
                    logger.error(f"Error al extraer el nombre de la alerta: {e}")
                    return

                try:
                    contrato_token = extraer_contrato_token(message)
                    if contrato_token is None:
                        logger.warning("No se pudo extraer el contrato del token.")
                        return
                    logger.debug(f'Contrato del token extraído: {contrato_token}')
                except Exception as e:
                    logger.error(f"Error al extraer el contrato del token: {e}")
                    return

                # Obtener el precio inicial del token
                try:
                    precio_inicial = obtener_precio_token(contrato_token)
                    if precio_inicial is None:
                        logger.warning(f"No se pudo obtener el precio inicial para el contrato: {contrato_token}")
                        return
                    logger.debug(f'Precio inicial extraído: {precio_inicial}')
                except Exception as e:
                    logger.error(f"Error al obtener el precio inicial: {e}")
                    return

                # Si todos los valores son correctos, almacenar la alerta
                timestamp = datetime.now()
                alerta_id = almacenar_alerta(nombre_alerta, contrato_token, precio_inicial)
                programar_actualizaciones(alerta_id, contrato_token, timestamp)
                logger.info(f'Alerta procesada y almacenada: {nombre_alerta} - {contrato_token}')
    except Exception as e:
        logger.error(f'Error al procesar el mensaje: {e}')

def main():
    # Configuración del bot
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Añadir manejador de mensajes y comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    agregar_manejadores(application)

    # Iniciar el checker en un hilo separado
    threading.Thread(target=bot_checker).start()

    # Iniciar el bot usando run_polling
    application.run_polling()

def bot_checker():
    """Checker que muestra un mensaje en la terminal cada X segundos indicando que el bot sigue vivo."""
    while True:
        logger.info("El bot está funcionando correctamente.")
        time.sleep(300)  # Cambia el tiempo (en segundos) según prefieras la frecuencia del mensaje

if __name__ == '__main__':
    main()
