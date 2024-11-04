import logging
import threading
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import config
from alert_parser import extraer_nombre_alerta, extraer_contrato_token
from database import almacenar_alerta
from price_updater import obtener_precio_token
from scheduler import iniciar_programador, programar_actualizaciones
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
        # Verificar que el mensaje y el texto no sean nulos
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
                nombre_alerta = extraer_nombre_alerta(message)
                contrato_token = extraer_contrato_token(message)
                precio_inicial = obtener_precio_token(contrato_token)
                timestamp = datetime.now()

                if nombre_alerta and contrato_token and precio_inicial:
                    alerta_id = almacenar_alerta(nombre_alerta, contrato_token, precio_inicial)
                    programar_actualizaciones(alerta_id, contrato_token, timestamp)
                    logger.info(f'Alerta procesada y almacenada: {nombre_alerta} - {contrato_token}')
                else:
                    logger.warning(f"Datos incompletos en el mensaje: {message}")
    except Exception as e:
        logger.error(f'Error al procesar el mensaje: {e}')

def main():
    # Configuración del bot
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Añadir manejador de mensajes y comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    agregar_manejadores(application)

    # Iniciar el programador en un hilo separado
    threading.Thread(target=iniciar_programador).start()

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