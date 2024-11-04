from telegram.ext import CommandHandler
from database import obtener_alertas

def rendimiento_command(update, context):
    command = update.message.text.split()[0][1:]
    args = context.args

    if len(args) != 1:
        update.message.reply_text(f'Uso correcto: /{command} nombre_de_la_alerta')
        return

    nombre_alerta = args[0]
    rendimiento = obtener_alertas(nombre_alerta)
    campo_rendimiento = f'rendimiento_{command.replace("rendimiento", "")}'

    if rendimiento:
        valor_rendimiento = rendimiento.get(campo_rendimiento)
        if valor_rendimiento is not None:
            mensaje = f"Rendimiento promedio a {campo_rendimiento[-2:]}h para '{nombre_alerta}': {valor_rendimiento:.2f}%"
        else:
            mensaje = f"No hay datos suficientes para '{nombre_alerta}'."
    else:
        mensaje = f"No se encontró información para la alerta '{nombre_alerta}'."

    update.message.reply_text(mensaje)

# Agregar el CommandHandler en main.py
def agregar_manejadores(dispatcher):
    dispatcher.add_handler(CommandHandler(['rendimiento1h', 'rendimiento6h', 'rendimiento12h', 'rendimiento24h', 'rendimiento72h'], rendimiento_command))