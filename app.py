from flask import Flask, jsonify
import os
import time
import requests
from datetime import datetime

# Variables para caché
cached_data = None
cache_timestamp = 0
cache_duration = 300  # Tiempo en segundos (5 minutos)

# Configuración de Flask
app = Flask(__name__)

# Función para obtener precios desde la API de ESIOS
def obtener_precios():
    try:
        # Configuración del endpoint y headers
        url = "https://api.esios.ree.es/indicators/1001"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": "d0217f0ebe4f45736f4bc1b4a14e46ab92d3bcd8e77336dfe0b428caec944368"  # Reemplaza con tu clave de API válida
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Procesar respuesta de la API
            json_data = response.json()
            valores = json_data.get("indicator", {}).get("values", [])
            
            # Filtrar por GeoID (ejemplo: Península)
            geo_id = 8741
            valores_filtrados = [v for v in valores if v["geo_id"] == geo_id]

            # Clasificar precios por franjas horarias y calcular estadísticas
            precios_por_hora = []
            precios = []
            for valor in valores_filtrados:
                hora = datetime.fromisoformat(valor["datetime"]).strftime("%H:%M")
                precio_eur_kwh = valor["value"] / 1000  # Convertir de €/MWh a €/kWh
                precios.append(precio_eur_kwh)

                # Clasificación por franjas horarias
                hora_actual = int(hora.split(":")[0])
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

            # Retornar datos procesados
            return {
                "resumen_precios": {
                    "precio_minimo": precio_minimo,
                    "precio_maximo": precio_maximo,
                    "precio_medio": precio_medio
                },
                "precios_por_hora": precios_por_hora
            }
        else:
            return {"error": f"Error al acceder a la API. Código de estado: {response.status_code}"}
    except Exception as e:
        print(f"Error en obtener_precios: {e}")
        return {"error": "Error interno en el servidor"}

# Función para obtener precios con caché
def obtener_precios_con_cache():
    global cached_data, cache_timestamp

    # Verifica si los datos están en caché y no han expirado
    if cached_data and (time.time() - cache_timestamp < cache_duration):
        print("Usando datos en caché")
        return cached_data

    # Si no hay caché o los datos han expirado, realiza la llamada a la API
    print("Llamando a la API para actualizar datos")
    datos = obtener_precios()
    if datos and "error" not in datos:
        cached_data = datos
        cache_timestamp = time.time()  # Actualiza el timestamp
    return datos

# Endpoint para obtener precios
@app.route("/api/precios", methods=["GET"])
def api_precios():
    datos = obtener_precios_con_cache()
    if datos and "error" not in datos:
        return jsonify(datos)
    else:
        return jsonify({"error": datos.get("error", "No se pudieron obtener los datos")}), 500

# Endpoint de bienvenida
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Bienvenido a la API de precios. Consulta /api/precios para obtener los datos."
    })

# Configuración del servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # Render asigna automáticamente un puerto
    app.run(debug=True, host="0.0.0.0", port=port)


