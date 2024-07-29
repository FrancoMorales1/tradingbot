from binance import Client
import pandas as pd
import numpy as np
import csv
import time
from joblib import load
import os
from dotenv import load_dotenv
import logging

def get_precision(symbol, client):
    try:
        info = client.get_symbol_info(symbol)
        filters = info['filters']
        for f in filters:
            if f['filterType'] == 'LOT_SIZE':
                step_size = f['stepSize']
                # Obtener el número de decimales
                precision = len(step_size.split('1')[0]) - 1
                return precision
    except Exception as e:
        print(f"Error obteniendo precisión: {e}")
        return 2  # Valor por defecto, ajusta según tus necesidades

def round_quantity(quantity, precision):
    return round(quantity, precision)

# Función para obtener las velas
def get_candles(client, symbol, interval, amount):
    try:
        klines = client.get_historical_klines(symbol, interval, f"{amount} minutes ago UTC")
        candles = [[float(c[1]), float(c[2]), float(c[3]), float(c[4])] for c in klines]
        return candles
    except Exception as e:
        logging.error(f"Error obteniendo velas: {e}")
        return []

# Función para tomar decisiones de trading
def decide_action(candles, decisionModel):
    try:
        sample = [float(c[0]) for c in candles]
        prediction = decisionModel.predict([sample])
        return prediction[0]
    except Exception as e:
        logging.error(f"Error tomando decisión: {e}")
        return None

# Función para realizar operaciones de trading
def execute_trade(client, symbol, action, usdt_balance, btc_balance, trade_percentage):
    try:
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        precision = get_precision(symbol, client)  # Obtener precisión del símbolo
        if action == 'Comprar':
            trade_amount_usdt = usdt_balance * trade_percentage
            trade_amount_btc = trade_amount_usdt / price
            trade_amount_btc = round_quantity(trade_amount_btc, precision)
            if trade_amount_btc > 0:
                # Ejecutar orden de compra
                order = client.order_market_buy(symbol=symbol, quantity=trade_amount_btc)
                print(f"Orden de compra ejecutada: {order}")

        elif action == 'Vender':
            trade_amount_btc = btc_balance * trade_percentage
            trade_amount_btc = round_quantity(trade_amount_btc, precision)
            if trade_amount_btc > 0:
                # Ejecutar orden de venta
                order = client.order_market_sell(symbol=symbol, quantity=trade_amount_btc)
                print(f"Orden de venta ejecutada: {order}")

    except Exception as e:
        logging.error(f"Error ejecutando trade: {e}")

# Función para cancelar ordenes de compra/venta pendientes
def cancel_open_orders(client, symbol):
    try:
        open_orders = client.get_open_orders(symbol=symbol)
        for order in open_orders:
            client.cancel_order(symbol=symbol, orderId=order['orderId'])
            print(f"Orden cancelada: {order}")
    except Exception as e:
        logging.error(f"Error cancelando órdenes: {e}")

# Configuración del cliente de Binance
load_dotenv()
API_KEY = os.getenv("TESTNET_API_KEY")
API_SECRET = os.getenv("TESTNET_API_SECRET")

client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'  # URL del testnet de Binance

decisionModel = load('../model/decisionModel.joblib')

symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1MINUTE

trade_percentage = 0.1  # Trade del 10%

log_file = 'trading_log.csv'
log_error_file = 'error_log.txt'
logging.basicConfig(filename=log_error_file, level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

sleep_interval = 60

# Abrir archivo CSV para guardar información
with open(f'../csv/{log_file}', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time', 'Open1', 'High1', 'Low1', 'Close1', 
                     'Open2', 'High2', 'Low2', 'Close2',
                     'Open3', 'High3', 'Low3', 'Close3', 
                     'Action', 'NextOpen', 'NextHigh', 'NextLow', 'NextClose'])  # Encabezados del archivo


while True:
    try:
        # Obtener información de la cuenta
        account_info = client.get_account()
        usdt_balance = 0
        btc_balance = 0

        # Extraer y mostrar los balances
        for balance in account_info['balances']:
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            if (total > 0) and (asset=='USDT' or asset=='BTC'):
                print(f'{asset}: {total}')
            if asset == 'USDT':
                usdt_balance = total
            elif asset == 'BTC':
                btc_balance = total

        # Obtener información de las velas de los últimos 3 minutos (por minuto)
        candles = get_candles(client, symbol, interval, 3)
        if not candles:
            time.sleep(sleep_interval)
            # Cancelar todas las órdenes pendientes
            cancel_open_orders(client, symbol)
            continue
        
        # Decidir si comprar, vender o no hacer nada
        action = decide_action(candles, decisionModel)
        
        print(f"Acción decidida: {action}")
        for candle in candles:
            print(f"Open: {candle[0]}, High: {candle[1]}, Low: {candle[2]}, Close: {candle[3]}")
        
        execute_trade(client, symbol, action, usdt_balance, btc_balance, trade_percentage)
        
        # Esperar un minuto antes de la siguiente iteración
        time.sleep(sleep_interval)

        # Cancelar todas las órdenes pendientes
        cancel_open_orders(client, symbol)

        # Obtener la vela del minuto siguiente para evaluación
        result = get_candles(client, symbol, interval, 1)

        # Guardar información en el archivo
        with open(f'../csv/{log_file}', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                pd.Timestamp.now(),
                *candles[0],  # Primera vela
                *candles[1],  # Segunda vela
                *candles[2],  # Tercera vela
                action,
                *result[0]  # Vela del minuto siguiente para evaluación
            ])
    except Exception as e:
        logging.error(f"Error en la iteración principal: {e}")
        time.sleep(sleep_interval)

        # Cancelar todas las órdenes pendientes
        cancel_open_orders(client, symbol)