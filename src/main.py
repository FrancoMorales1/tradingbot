import pandas as pd
import csv
import time
import logging

from services.binance_services import create_binance_client, get_account_info, get_candles, execute_trade, cancel_open_orders
from model.model_services import load_model, decide_action
from config.config import log_file_path, log_error_file_path, symbol, interval, trade_amount_btc, sleep_interval

# Configuración del logging
logging.basicConfig(filename=log_error_file_path, level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Crear cliente de Binance
client = create_binance_client()

# Cargar modelo de decisión
model_open = load_model('./model/models_created/model_open.joblib')
model_high = load_model('./model/models_created/model_high.joblib')
model_low = load_model('./model/models_created/model_low.joblib')
model_close = load_model('./model/models_created/model_close.joblib')

# Abrir archivo CSV para guardar información
with open(log_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time', 'Open1', 'High1', 'Low1', 'Close1', 
                     'Open2', 'High2', 'Low2', 'Close2',
                     'Open3', 'High3', 'Low3', 'Close3', 
                     'Action', 'NextOpen', 'NextHigh', 'NextLow', 'NextClose', 'Decision Correcta',
                     'USDT Balance', 'BTC Balance', 'Total Value USDT'])

while True:
    try:
        # Obtener información de la cuenta
        usdt_balance, btc_balance = get_account_info(client)
        
        # Obtener información de las velas de los últimos 3 minutos (por minuto)
        candles = get_candles(client, symbol, interval, 3)
        if not candles:
            # Cancelar todas las órdenes pendientes
            cancel_open_orders(client, symbol)
            continue
        
        # Decidir si comprar, vender o no hacer nada
        action_open = decide_action(candles, model_open)
        action_high = decide_action(candles, model_high)
        action_low = decide_action(candles, model_low)
        action_close = decide_action(candles, model_close)

        array_action = [action_open, action_high, action_low, action_close]
        comprar_count = array_action.count('Comprar')
        vender_count = array_action.count('Vender')
        nada_count = array_action.count('Nada')

        # Determinar la acción más frecuente
        if comprar_count > vender_count and comprar_count > nada_count:
            final_action = 'Comprar'
        elif vender_count > comprar_count and vender_count > nada_count:
            final_action = 'Vender'
        elif nada_count > comprar_count and nada_count > vender_count:
            final_action = 'Nada'
        else:
            final_action = 'Nada'  # En caso de empate

        execute_trade(client, symbol, final_action, trade_amount_btc)
        
        # Esperar un minuto antes de la siguiente iteración
        time.sleep(sleep_interval)

        # Cancelar todas las órdenes pendientes
        cancel_open_orders(client, symbol)

        # Obtener la vela del minuto siguiente para evaluación
        result = get_candles(client, symbol, interval, 1)[0]

        # Calcular el valor total en USDT
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        total_value_usdt = usdt_balance + (btc_balance * price)

        # Determinar si la decisión fue correcta
        max_open_candle = max([float(c[0]) for c in candles])
        close_result = result[3]

        if max_open_candle < close_result:
            decision_correcta = 'Vender'
        elif max_open_candle > close_result:
            decision_correcta = 'Comprar'
        else:
            decision_correcta = 'Nada'

        # Guardar información en el archivo y actualizar el array de los últimos 10 registros
        new_record = [
            pd.Timestamp.now(),
            *candles[0],  # Primera vela
            *candles[1],  # Segunda vela
            *candles[2],  # Tercera vela
            final_action,
            *result,  # Vela del minuto siguiente para evaluación
            decision_correcta,
            usdt_balance,
            btc_balance,
            total_value_usdt
        ]
        
        # Guardar información en el archivo
        with open(log_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_record)
        
    except Exception as e:
        logging.error(f"Error en la iteración principal: {e}")

        # Cancelar todas las órdenes pendientes
        cancel_open_orders(client, symbol)