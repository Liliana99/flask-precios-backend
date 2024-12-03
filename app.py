from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Función para realizar scraping
def obtener_precios():
    try:

        url = 'https://preciosdelaluz.es/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        respuesta = requests.get(url, headers=headers)
        if respuesta.status_code == 200:
            sopa = BeautifulSoup(respuesta.text, 'html.parser')
            resumen = sopa.find('div', class_='bloqueresumen')

            if not resumen:
                return {'error': 'No se pudo encontrar el resumen'}

            # Extraer precios
            precio_minimo = resumen.find('div', class_='preciomin').find('span').text.strip()
            precio_medio = resumen.find('div', class_='preciomed').find('span').text.strip()
            precio_maximo = resumen.find('div', class_='preciomax').find('span').text.strip()

            # Estructura para devolver los precios mínimos, medios y máximos
            resumen_precios = {
                'precio_minimo': f"{precio_minimo} €/kWh",
                'precio_medio': f"{precio_medio} €/kWh",
                'precio_maximo': f"{precio_maximo} €/kWh",
            }

            # Extraer precios horarios
        bloques = sopa.select('div.precitem')  # Selector para los elementos por hora
        precios_horarios = []

        for bloque in bloques:
            hora = bloque.find('span', class_='hora').text.strip()  # Extraer hora
            precio = bloque.find('span', class_='euritos').text.strip()  # Extraer precio
            precios_horarios.append({'hora': hora, 'precio': f"{precio} €/kWh"})

        # Combinar todos los resultados
        return {
            'resumen_precios': resumen_precios,
            'precios_horarios': precios_horarios
        }
        

   
    except Exception as e:
        print(f"Error en obtener_precios: {e}")
        return {'error': 'Error interno en el servidor'}

# Endpoint que expone los datos
@app.route('/api/precios', methods=['GET'])
def api_precios():
    datos = obtener_precios()
    if datos and 'error' not in datos:
        return jsonify(datos)
    else:
        return jsonify({'error': 'No se pudieron obtener los datos'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  
    app.run(debug=True, host='0.0.0.0', port=port)

