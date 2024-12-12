import requests
from datetime import datetime

# Configuración
url = 'https://api.esios.ree.es/indicators/1001'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'x-api-key': 'd0217f0ebe4f45736f4bc1b4a14e46ab92d3bcd8e77336dfe0b428caec944368'
}

# GeoID para Península
geo_id = 8741

# Hacer la petición
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Convertir la respuesta a JSON
    json_data = response.json()
    valores = json_data.get('indicator', {}).get('values', [])

    # Filtrar por GeoID
    valores_filtrados = [v for v in valores if v['geo_id'] == geo_id]

    # Convertir precios y clasificar por franjas horarias
    precios_por_hora = []
    precios = []
    for valor in valores_filtrados:
        hora = datetime.fromisoformat(valor['datetime']).strftime('%H:%M')
        precio_eur_kwh = valor['value'] / 1000  # Convertir de €/MWh a €/kWh
        precios.append(precio_eur_kwh)

        # Clasificación por franjas horarias
        hora_actual = int(hora.split(':')[0])
        if 0 <= hora_actual < 8:
            franja = "Valle"
        elif 8 <= hora_actual < 10 or 14 <= hora_actual < 18 or 22 <= hora_actual < 24:
            franja = "Llano"
        else:
            franja = "Punta"

        precios_por_hora.append({
            "hora": hora,
            "precio": round(precio_eur_kwh, 3),
            "franja": franja
        })

    # Calcular estadísticas generales
    precio_minimo = round(min(precios), 3)
    precio_maximo = round(max(precios), 3)
    precio_medio = round(sum(precios) / len(precios), 3)

    # Resultado final
    resultado = {
        "resumen_precios": {
            "precio_minimo": precio_minimo,
            "precio_maximo": precio_maximo,
            "precio_medio": precio_medio
        },
        "precios_por_hora": precios_por_hora
    }

    # Mostrar el resultado
    print("\nResumen de Precios:")
    print(f"Precio Mínimo: {precio_minimo} €/kWh")
    print(f"Precio Máximo: {precio_maximo} €/kWh")
    print(f"Precio Medio: {precio_medio} €/kWh\n")

    print("Precios por Hora:")
    for precio in precios_por_hora:
        print(f"Hora: {precio['hora']} - Precio: {precio['precio']} €/kWh - Franja: {precio['franja']}")

else:
    print(f"Error al obtener datos: {response.status_code}")

