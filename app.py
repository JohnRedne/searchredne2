# -*- coding: utf-8 -*-
"""Untitled37.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12ltdYIH4U3gXuystpkRQUnaCYaHBlvnw
"""

from flask import Flask, request, jsonify, send_file
import urllib.request
import io
from obspy import read, UTCDateTime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Función para convertir una fecha ISO8601 a día juliano
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
        start_date_input = request.args.get("start")
        end_date_input = request.args.get("end")
        net = request.args.get("net")
        sta = request.args.get("sta")

        # Canales y colores predefinidos
        channels = ["HNE.D", "HNN.D", "HNZ.D"]
        colors = ["blue", "green", "red"]

        # Validar los parámetros
        if not all([start_date_input, end_date_input, net, sta]):
            return jsonify({"error": "Faltan parámetros requeridos (start, end, net, sta)."}), 400

        # Validar formato de las fechas
        try:
            start_date = datetime.fromisoformat(start_date_input)
            end_date = datetime.fromisoformat(end_date_input)
        except ValueError:
            return jsonify({"error": "El formato de la fecha debe ser ISO8601 (ej: 2024-12-30T21:01:00)."}), 400

        # Ajustar si las horas son iguales
        if start_date == end_date:
            start_date += timedelta(seconds=20)
            end_date -= timedelta(seconds=10)

        # Limitar el intervalo a 15 minutos
        if (end_date - start_date) > timedelta(minutes=15):
            end_date = start_date + timedelta(minutes=15)

        # Convertir fecha de inicio al día juliano
        julian_day = date_to_julian_day(start_date.isoformat())
        year = start_date.year

        streams = {}
        urls = {}
        for channel in channels:
            # Construir la URL del archivo MiniSEED
            url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{year}/{net}/{sta}/{channel}/{net}.{sta}.00.{channel}.{year}.{julian_day}"
            urls[channel] = url

            # Descargar y leer el archivo MiniSEED
            try:
                print(f"Descargando datos desde: {url}")
                response = urllib.request.urlopen(url)
                stream = read(io.BytesIO(response.read()))
                streams[channel] = stream
            except Exception as e:
                print(f"Error al descargar o procesar datos para {channel}: {e}")
                return jsonify({"error": f"No se pudo procesar el canal {channel}: {e}"}), 500

        # Crear variable para la fecha
        date_str = start_date.strftime('%b-%d-%Y')

        # Graficar los datos de los sismogramas
        fig, axes = plt.subplots(len(channels), 1, figsize=(12, 12), sharex=False)
        plt.subplots_adjust(hspace=0.5)

        for i, (channel, color) in enumerate(zip(channels, colors)):
            trace = streams[channel][0]

            # Convertir fechas de recorte a UTCDateTime
            start_utc = UTCDateTime(start_date)
            end_utc = UTCDateTime(end_date)

            # Recortar los datos al intervalo definido por el usuario
            stream = streams[channel].slice(starttime=start_utc, endtime=end_utc)
            trace = stream[0]

            ax = axes[i]
            ax.plot(trace.times("matplotlib"), trace.data, label=f"Canal {channel}", linewidth=0.8, color=color)
            ax.set_title(f"Sismograma {channel} ({trace.stats.station})", fontsize=12)
            ax.set_ylabel("Amplitud", fontsize=10)
            ax.legend(loc="upper right")
            ax.grid(True, linestyle="--", alpha=0.7)

            # Formatear el eje X para mostrar tiempos en UTC en cada gráfico
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S UTC'))

            # Mostrar el URL asociado debajo de cada gráfico
            ax.text(0.5, -0.2, f"URL ({channel}): {urls[channel]}", transform=ax.transAxes, fontsize=8, color=color, ha="center")

            # Ajustar etiquetas para el último gráfico
            if i == len(channels) - 1:
                ax.set_xlabel("Tiempo (HH:MM:SS UTC)", fontsize=10)

        # Mostrar la fecha debajo de todos los sismogramas
        plt.figtext(0.5, 0.01, f"Fecha: {date_str}", wrap=True, horizontalalignment='center', fontsize=12)

        # Guardar la imagen en memoria
        output_image = io.BytesIO()
        plt.savefig(output_image, format='png', bbox_inches="tight")
        output_image.seek(0)
        plt.close(fig)

        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({"error": f"Ocurrió un error durante el procesamiento: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Obtén el puerto desde las variables de entorno
    app.run(host='0.0.0.0', port=5000)










