# -*- coding: utf-8 -*-
"""Untitled37.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12ltdYIH4U3gXuystpkRQUnaCYaHBlvnw
"""

from flask import Flask, request, jsonify, send_file
import requests
import io
from obspy import read
import matplotlib.pyplot as plt
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def date_to_julian_day(date: str) -> int:
    """Convierte una fecha ISO8601 al día juliano del año."""
    dt = datetime.fromisoformat(date)
    start_of_year = datetime(dt.year, 1, 1)
    julian_day = (dt - start_of_year).days + 1
    return julian_day

@app.route('/generate_sismograma', methods=['GET'])
def generate_sismograma():
    try:
        print(f"Solicitud recibida: {request.args}")  # Log inicial de la solicitud

        # Obtener parámetros de la solicitud
        start = request.args.get('start')
        end = request.args.get('end')
        net = request.args.get('net')
        sta = request.args.get('sta')
        channel = request.args.get('channel', 'HNE.D')  # Canal por defecto

        if not all([start, end, net, sta]):
            print("Parámetros faltantes")  # Log para parámetros faltantes
            return jsonify({"error": "Faltan parámetros requeridos (start, end, net, sta)"}), 400

        # Convertir fecha de inicio al día juliano
        julian_day = date_to_julian_day(start)
        year = datetime.fromisoformat(start).year

        # Base URL
        base_url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{year}/{net}/{sta}"

        # Crear enlace para el canal
        url = f"{base_url}/{channel}/{net}.{sta}.00.{channel}.{year}.{julian_day}"

        print(f"URL generada: {url}")  # Log de la URL generada

        # Descargar y procesar los datos
        try:
            print(f"Descargando datos desde: {url}")  # Log de la descarga
            response = requests.get(url, timeout=150)
            if response.status_code != 200:
                raise Exception(f"Error {response.status_code} al descargar el archivo {url}")

            # Leer el archivo MiniSEED desde memoria
            stream = read(io.BytesIO(response.content))
            print(f"Datos procesados para el canal {channel}")  # Log de procesamiento exitoso

        except Exception as e:
            print(f"Error procesando {channel}: {e}")  # Log del error específico
            return jsonify({"error": f"Error procesando {channel}: {str(e)}"}), 500

        # Graficar los datos
        fig, ax = plt.subplots(figsize=(12, 5))
        trace = stream[0]
        ax.plot(trace.times("matplotlib"), trace.data, label=f"Canal {channel}", color='blue')
        ax.set_title(f"Sismograma {channel}")
        ax.set_xlabel("Tiempo (UTC)")
        ax.set_ylabel("Amplitud")
        ax.grid()
        ax.legend()

        plt.tight_layout()

        # Guardar y enviar la imagen
        output_image = io.BytesIO()
        plt.savefig(output_image, format='png')
        output_image.seek(0)
        plt.close(fig)

        print("Imagen generada exitosamente")  # Log de éxito

        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        print(f"Error general: {e}")  # Log del error general
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)







