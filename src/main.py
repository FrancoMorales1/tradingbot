import pandas as pd
import csv
import time
import logging

from services.binance_services import create_binance_client, get_account_info, get_candles, execute_trade, cancel_open_orders
from model.model_services import load_model, decide_action
from config.config import log_file_path, log_error_file_path, symbol, interval, trade_percentage, sleep_interval

# Configuración del logging
logging.basicConfig(filename=log_error_file_path, level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Crear cliente de Binance
client = create_binance_client()

# Cargar modelo de decisión
decisionModel = load_model('./model/decisionModel.joblib')

last_10_records = []

# Abrir archivo CSV para guardar información
with open(log_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time', 'Open1', 'High1', 'Low1', 'Close1', 
                     'Open2', 'High2', 'Low2', 'Close2',
                     'Open3', 'High3', 'Low3', 'Close3', 
                     'Action', 'NextOpen', 'NextHigh', 'NextLow', 'NextClose',
                     'USDT_Balance', 'BTC_Balance', 'Total_USDT_Value'])
    
while True:
    try:
        # Obtener información de la cuenta
        usdt_balance, btc_balance = get_account_info(client)
        
        # Obtener información de las velas de los últimos 3 minutos (por minuto)
        candles = get_candles(client, symbol, interval, 3)
        if not candles:
            time.sleep(sleep_interval)
            # Cancelar todas las órdenes pendientes
            cancel_open_orders(client, symbol)
            continue
        
        # Decidir si comprar, vender o no hacer nada
        action = decide_action(candles, decisionModel)
        
        execute_trade(client, symbol, action, usdt_balance, btc_balance, trade_percentage)
        
        # Esperar un minuto antes de la siguiente iteración
        time.sleep(sleep_interval)

        # Cancelar todas las órdenes pendientes
        cancel_open_orders(client, symbol)

        # Obtener la vela del minuto siguiente para evaluación
        result = get_candles(client, symbol, interval, 1)

        # Calcular el valor total en USDT
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        total_value_usdt = usdt_balance + (btc_balance * price)
        
        # Guardar información en el archivo y actualizar el array de los últimos 10 registros
        new_record = [
            pd.Timestamp.now(),
            *candles[0],  # Primera vela
            *candles[1],  # Segunda vela
            *candles[2],  # Tercera vela
            action,
            *result[0],  # Vela del minuto siguiente para evaluación
            usdt_balance,
            btc_balance,
            total_value_usdt
        ]
        
        # Guardar información en el archivo
        with open(log_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_record)
        
         # Actualizar el array de los últimos 10 registros
        last_10_records.append(new_record)
        if len(last_10_records) > 10:
            last_10_records.pop(0)
        
        print(last_10_records)
        
    except Exception as e:
        logging.error(f"Error en la iteración principal: {e}")
        time.sleep(sleep_interval)

        # Cancelar todas las órdenes pendientes
        cancel_open_orders(client, symbol)