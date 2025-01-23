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
        print(f"Solicitud recibida: {request.args}")

        # Parámetros fijos
        channel = "HNE.D"
        url = "http://osso.univalle.edu.co/apps/seiscomp/archive/2024/UX/UIS01/HNE.D/UX.UIS01.00.HNE.D.2024.330"

        print(f"URL generada: {url}")

        # Descargar datos
        print(f"Intentando descargar datos desde: {url}")
        response = requests.get(url, timeout=150)
        print(f"Estado de la respuesta: {response.status_code}")

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code} al descargar el archivo {url}")

        print("Datos descargados exitosamente.")

        # Leer archivo MiniSEED
        print("Intentando leer el archivo MiniSEED...")
        stream = read(io.BytesIO(response.content))
        print(f"Datos procesados para el canal {channel}: {stream[0].stats}")

        # Graficar los datos
        print("Generando gráfico...")
        fig, ax = plt.subplots(figsize=(12, 6))
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

        print("Imagen generada exitosamente.")
        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)








