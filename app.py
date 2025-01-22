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

app = Flask(__name__)

def date_to_julian_day(date: str) -> int:
    """Convierte una fecha ISO8601 al día juliano del año."""
    dt = datetime.fromisoformat(date)
    start_of_year = datetime(dt.year, 1, 1)
    julian_day = (dt - start_of_year).days + 1
    return julian_day

@app.route('/generate_sismograma', methods=['GET'])
def generate_sismograma():
    try:
        # Obtener parámetros de la solicitud
        start = request.args.get('start')  # Fecha de inicio en ISO8601
        end = request.args.get('end')      # Fecha de fin en ISO8601
        net = request.args.get('net')      # Red (por ejemplo, "UX")
        sta = request.args.get('sta')      # Estación (por ejemplo, "UIS01")
        channels = ['HNE.D', 'HNN.D', 'HNZ.D']  # Lista de canales

        # Validar parámetros
        if not all([start, end, net, sta]):
            return jsonify({"error": "Faltan parámetros requeridos (start, end, net, sta)"}), 400

        # Convertir fecha de inicio al día juliano
        julian_day = date_to_julian_day(start)
        year = datetime.fromisoformat(start).year

        # Base URL para los datos MiniSEED
        base_url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{year}/{net}/{sta}"

        # Crear una lista de URLs para los canales
        urls = [
            f"{base_url}/{channel}/{net}.{sta}.00.{channel}.{year}.{julian_day}"
            for channel in channels
        ]

        # Descargar y procesar los datos de cada canal
        streams = {}
        for channel, url in zip(channels, urls):
            print(f"Accediendo a: {url}")
            response = requests.get(url, timeout=150)
            if response.status_code != 200:
                return jsonify({"error": f"Error al descargar datos para el canal {channel}: {response.status_code}"}), 500

            streams[channel] = read(io.BytesIO(response.content))

        # Crear gráficos combinados
        fig, axes = plt.subplots(len(channels), 1, figsize=(12, 10))
        for idx, (channel, stream) in enumerate(streams.items()):
            trace = stream[0]
            axes[idx].plot(trace.times("matplotlib"), trace.data, label=f"Canal {channel}", color='blue')
            axes[idx].set_title(f"Sismograma {channel} ({sta})")
            axes[idx].set_xlabel("Tiempo (UTC)")
            axes[idx].set_ylabel("Amplitud")
            axes[idx].grid()
            axes[idx].legend()

        plt.tight_layout()

        # Guardar la imagen en memoria y devolverla
        output_image = io.BytesIO()
        plt.savefig(output_image, format='png')
        output_image.seek(0)
        plt.close(fig)

        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



