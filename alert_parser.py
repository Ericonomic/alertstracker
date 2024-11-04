import re

def extraer_nombre_alerta(message):
    # Buscar el nombre de la alerta después del símbolo "➡️" y antes de "|"
    match = re.search(r'➡️\s+(.+?)\s+\|', message)
    return match.group(1).strip() if match else None

def extraer_contrato_token(message):
    # Buscar el contrato del token: una cadena alfanumérica larga seguida del símbolo "✂️"
    match = re.search(r'\n([A-Za-z0-9]{35,})✂️', message)
    return match.group(1).strip() if match else None