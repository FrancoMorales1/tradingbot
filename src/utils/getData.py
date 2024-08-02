import os
import csv
import time
from datetime import datetime, timedelta
from binance import Client
from joblib import dump
from dotenv import load_dotenv
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

# Cargar las variables de entorno
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Inicializar el cliente de Binance
client = Client(API_KEY, API_SECRET)
# client.API_URL = 'https://testnet.binance.vision/api'

# Definir el símbolo y el intervalo
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1MINUTE  # Intervalo diario

# Definir la fecha de inicio y fin
end_time = datetime.now()
start_time = end_time - timedelta(days=730)

# Convertir las fechas a timestamps
start_timestamp = int(time.mktime(start_time.timetuple()) * 1000)
end_timestamp = int(time.mktime(end_time.timetuple()) * 1000)

# Obtener datos históricos
klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

# Guardar los datos en un archivo CSV
csv_file = 'btc_price_data.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time'])
    for kline in klines:
        writer.writerow(kline[:7])  # Escribir solo las primeras 7 columnas

print(f'Datos guardados en {csv_file}')