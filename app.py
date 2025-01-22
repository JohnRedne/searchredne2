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

app = Flask(__name__)

@app.route('/generate_sismograma', methods=['GET'])
def generate_sismograma():
    try:
        # Obtener parámetros
        start = request.args.get('start')
        end = request.args.get('end')
        net = request.args.get('net')
        sta = request.args.get('sta')
        channels = ['HNE.D', 'HNN.D', 'HNZ.D']  # Lista de canales

        # Validar parámetros
        if not all([start, end, net, sta]):
            return jsonify({"error": "Faltan parámetros requeridos"}), 400

        # Base URL para los datos MiniSEED
        #url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{start[:4]}/{net}/{sta}/{cha}/{net}.{sta}.{loc}.{cha}.{start[:4]}.{start[5:7]}"
        base_url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{start[:4]}/{net}/{sta}/"

        # Descargar y procesar datos de cada canal
        streams = {}
        for channel in channels:
            # Construir el enlace para cada canal
            url = f"{base_url}{channel}/{net}.{sta}.00.{channel}.{start[:4]}.{start[5:7]}"
            print(f"Accediendo a: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                return jsonify({"error": f"Error al descargar datos para el canal {channel}: {response.status_code}"}), 500
            streams[channel] = read(io.BytesIO(response.content))

        # Crear gráficos combinados
        fig, axes = plt.subplots(len(channels), 1, figsize=(12, 10))
        for idx, (channel, stream) in enumerate(streams.items()):
            tr = stream[0]
            axes[idx].plot(tr.times("matplotlib"), tr.data, label=f"Canal {channel}", color='blue')
            axes[idx].set_title(f"Sismograma {channel} ({sta})")
            axes[idx].set_ylabel("Amplitud")
            axes[idx].legend()
            axes[idx].grid()
        plt.xlabel("Tiempo (HH:MM:SS UTC)")
        plt.tight_layout()

        # Guardar la imagen en memoria y enviarla como respuesta
        output_image = io.BytesIO()
        plt.savefig(output_image, format='png')
        output_image.seek(0)
        plt.close(fig)

        return send_file(output_image, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
