from binance import Client
import logging
import time
from utils.utils import get_precision, round_quantity

def create_binance_client():
    from config.config import API_KEY, API_SECRET, API_URL
    client = Client(API_KEY, API_SECRET)
    client.API_URL = API_URL
    return client

    
def get_account_info(client):
    try:
        account_info = client.get_account()
        usdt_balance = 0
        btc_balance = 0
        for balance in account_info['balances']:
            asset = balance['asset']
            total = float(balance['free']) + float(balance['locked'])
            if asset == 'USDT':
                usdt_balance = total
            elif asset == 'BTC':
                btc_balance = total
        return usdt_balance, btc_balance
    except Exception as e:
        logging.error(f"Error obteniendo información de la cuenta: {e}")
        return 0, 0

def get_candles(client, symbol, interval, amount):
    try:
        klines = client.get_historical_klines(symbol, interval, f"{amount} minutes ago UTC")
        return [[float(c[1]), float(c[2]), float(c[3]), float(c[4])] for c in klines]
    except Exception as e:
        logging.error(f"Error obteniendo velas: {e}")
        return []

def execute_trade(client, symbol, action, usdt_balance, btc_balance, trade_percentage):
    try:
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        precision = get_precision(symbol, client)
        if action == 'Comprar':
            trade_amount_usdt = usdt_balance * trade_percentage
            trade_amount_btc = trade_amount_usdt / price
            trade_amount_btc = round_quantity(trade_amount_btc, precision)
            if trade_amount_btc > 0:
                order = client.order_market_buy(symbol=symbol, quantity=trade_amount_btc)
                logging.info(f"Orden de compra ejecutada: {order}")
        elif action == 'Vender':
            trade_amount_btc = btc_balance * trade_percentage
            trade_amount_btc = round_quantity(trade_amount_btc, precision)
            if trade_amount_btc > 0:
                order = client.order_market_sell(symbol=symbol, quantity=trade_amount_btc)
                logging.info(f"Orden de venta ejecutada: {order}")
    except Exception as e:
        logging.error(f"Error ejecutando trade: {e}")

def cancel_open_orders(client, symbol):
    try:
        open_orders = client.get_open_orders(symbol=symbol)
        for order in open_orders:
            client.cancel_order(symbol=symbol, orderId=order['orderId'])
            logging.info(f"Orden cancelada: {order}")
    except Exception as e:
        logging.error(f"Error cancelando órdenes: {e}")