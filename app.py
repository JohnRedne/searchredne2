# -*- coding: utf-8 -*-
"""Untitled37.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12ltdYIH4U3gXuystpkRQUnaCYaHBlvnw
"""

from flask import Flask, request, jsonify, send_file
import urllib.request
import io
from obspy import read
import matplotlib.pyplot as plt
import os
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
        # Obtener parámetros de la solicitud
        start = request.args.get('start')
        end = request.args.get('end')
        net = request.args.get('net')
        sta = request.args.get('sta')
        channels = ['HNE.D', 'HNN.D', 'HNZ.D']

        if not all([start, end, net, sta]):
            return jsonify({"error": "Faltan parámetros requeridos (start, end, net, sta)"}), 400

        # Convertir fecha de inicio al día juliano
        julian_day = date_to_julian_day(start)
        year = datetime.fromisoformat(start).year

        # Base URL
        base_url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{year}/{net}/{sta}"

        # Crear enlaces para los canales
        urls = {
            channel: f"{base_url}/{channel}/{net}.{sta}.00.{channel}.{year}.{julian_day}"
            for channel in channels
        }

        streams = {}

        # Descargar y procesar los datos
        for channel, url in urls.items():
            temp_file = f"{channel}.mseed"
            try:
                # Descargar al disco
                urllib.request.urlretrieve(url, temp_file)
                print(f"Archivo descargado: {temp_file}")

                # Leer con ObsPy
                streams[channel] = read(temp_file)
                os.remove(temp_file)

            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return jsonify({"error": f"Error procesando {channel}: {str(e)}"}), 500

        # Graficar los datos
        fig, axes = plt.subplots(len(channels), 1, figsize=(12, 10))
        for idx, (channel, stream) in enumerate(streams.items()):
            trace = stream[0]
            axes[idx].plot(trace.times("matplotlib"), trace.data, label=f"Canal {channel}", color='blue')
            axes[idx].set_title(f"Sismograma {channel}")
            axes[idx].set_xlabel("Tiempo (UTC)")
            axes[idx].set_ylabel("Amplitud")
            axes[idx].grid()
            axes[idx].legend()

        plt.tight_layout()

        # Guardar y enviar la imagen
        output_image = io.BytesIO()
        plt.savefig(output_image, format='png')
        output_image.seek(0)
        plt.close(fig)

        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)






