from binance import Client
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TESTNET_API_KEY")
API_SECRET = os.getenv("TESTNET_API_SECRET")
API_URL = 'https://testnet.binance.vision/api'  # URL del testnet de Binance

symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1MINUTE
sleep_interval = 60
trade_amount_btc = 0.001

log_file_path = './logs/trading_log.csv'
log_error_file_path = './logs/error_log.txt'
