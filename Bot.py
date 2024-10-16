# To test or purchase the source code, contact @SolVolSupp_bot on Telegram
# To test or purchase the source code, contact @SolVolSupp_bot on Telegram

import requests
import asyncio
import pandas as pd

from apscheduler.schedulers.background import BlockingScheduler

from soltrade.transactions import perform_swap, market
from soltrade.indicators import calculate_ema, calculate_rsi, calculate_bbands, calculate_macd, calculate_stoch
from soltrade.wallet import find_balance, check_wallet_status, transfer_funds, get_wallet_transactions
from soltrade.log import log_general, log_transaction
from soltrade.config import config

market('position.json')

# Pulls the candlestick information in fifteen minute intervals
def fetch_candlestick() -> dict:
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': config().api_key}
    params = {'tsym': config().primary_mint_symbol, 'fsym': config().secondary_mint_symbol, 'limit': 50, 'aggregate': config().trading_interval_minutes}
    response = requests.get(url, headers=headers, params=params)
    if response.json().get('Response') == 'Error':
        log_general.error(response.json().get('Message'))
        exit()
    return response.json()

# Analyzes the current market variables and determines trades
def perform_analysis():
    log_general.debug("Soltrade is analyzing the market; no trade has been executed.")

    global stoploss, takeprofit

    market().load_position()

    # Converts JSON response for DataFrame manipulation
    candle_json = fetch_candlestick()
    candle_dict = candle_json["Data"]["Data"]

    # Creates DataFrame for manipulation
    columns = ['close', 'high', 'low', 'open', 'time', 'VF', 'VT']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # DataFrame variable for TA-Lib manipulation
    cl = df['close']

    # Technical analysis values used in trading algorithm
    price = cl.iat[-1]
    ema_short = calculate_ema(dataframe=df, length=5)
    ema_medium = calculate_ema(dataframe=df, length=20)
    rsi = calculate_rsi(dataframe=df, length=14)
    upper_bb, lower_bb = calculate_bbands(dataframe=df, length=14)
    macd, signal, hist = calculate_macd(dataframe=df)
    stoch_k, stoch_d = calculate_stoch(dataframe=df)
    stoploss = market().sl
    takeprofit = market().tp

    log_general.debug(f"""
price:                  {price}
short_ema:              {ema_short}
med_ema:                {ema_medium}
upper_bb:               {upper_bb.iat[-1]}
lower_bb:               {lower_bb.iat[-1]}
rsi:                    {rsi}
macd:                   {macd.iat[-1]}
signal:                 {signal.iat[-1]}
stoch_k:                {stoch_k.iat[-1]}
stoch_d:                {stoch_d.iat[-1]}
stop_loss:              {stoploss}
take_profit:            {takeprofit}
""")

    if not market().position:
        input_amount = find_balance(config().primary_mint)

        if (ema_short > ema_medium or price < lower_bb.iat[-1]) and rsi <= 31:
            log_transaction.info("Soltrade has detected a buy signal.")
            if input_amount <= 0:
                log_transaction.warning(f"Soltrade has detected a buy signal, but does not have enough {config().primary_mint_symbol} to trade.")
                return
            is_swapped = asyncio.run(perform_swap(input_amount, config().primary_mint))
            if is_swapped:
                stoploss = market().sl = cl.iat[-1] * 0.925
                takeprofit = market().tp = cl.iat[-1] * 1.25
                market().update_position(True, stoploss, takeprofit)
            return
    else:
        input_amount = find_balance(config().secondary_mint)

        if price <= stoploss or price >= takeprofit:
            log_transaction.info("Soltrade has detected a sell signal. Stoploss or takeprofit has been reached.")
            is_swapped = asyncio.run(perform_swap(input_amount, config().secondary_mint))
            if is_swapped:
                stoploss = takeprofit = market().sl = market().tp = 0
                market().update_position(False, stoploss, takeprofit)
            return

        if (ema_short < ema_medium or price > upper_bb.iat[-1]) and rsi >= 68:
            log_transaction.info("Soltrade has detected a sell signal. EMA or BB has been reached.")
            is_swapped = asyncio.run(perform_swap(input_amount, config().secondary_mint))
            if is_swapped:
                stoploss = takeprofit = market().sl = market().tp = 0
                market().update_position(False, stoploss, takeprofit)
            return

# Fetch market data for specified intervals
def fetch_market_data(interval: str = 'histoday') -> dict:
    url = f"https://min-api.cryptocompare.com/data/v2/{interval}"
    headers = {'authorization': config().api_key}
    params = {'tsym': config().primary_mint_symbol, 'fsym': config().secondary_mint_symbol, 'limit': 200}
    response = requests.get(url, headers=headers, params=params)
    if response.json().get('Response') == 'Error':
        log_general.error(response.json().get('Message'))
        exit()
    return response.json()

# Calculate Moving Average Convergence Divergence
def calculate_macd(dataframe: pd.DataFrame, short_period: int = 12, long_period: int = 26, signal_period: int = 9):
    short_ema = dataframe['close'].ewm(span=short_period, adjust=False).mean()
    long_ema = dataframe['close'].ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

# Calculate Stochastic Oscillator
def calculate_stoch(dataframe: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    low_min = dataframe['low'].rolling(window=k_period).min()
    high_max = dataframe['high'].rolling(window=k_period).max()
    k = 100 * ((dataframe['close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    return k, d

# Check wallet status
def check_wallet_status(wallet_address: str):
    # Simulated function to check wallet status
    return {"address": wallet_address, "status": "active"}

# Transfer funds between wallets
def transfer_funds(from_wallet: str, to_wallet: str, amount: float):
    # Simulated function to transfer funds
    log_transaction.info(f"Transferring {amount} from {from_wallet} to {to_wallet}.")
    return True

# Get wallet transactions
def get_wallet_transactions(wallet_address: str) -> list:
    # Simulated function to get wallet transactions
    return [{"txid": "12345", "amount": 0.5, "type": "deposit"}, {"txid": "67890", "amount": 0.3, "type": "withdrawal"}]

# Log wallet transactions
def log_wallet_transactions(wallet_address: str):
    transactions = get_wallet_transactions(wallet_address)
    for transaction in transactions:
        log_general.info(f"Wallet {wallet_address} - TxID: {transaction['txid']}, Amount: {transaction['amount']}, Type: {transaction['type']}")

# Analyze market sentiment
def analyze_market_sentiment():
    # Simulated function to analyze market sentiment
    sentiment = "Bullish"
    log_general.info(f"Market sentiment is currently {sentiment}.")
    return sentiment

# Update trading parameters
def update_trading_parameters():
    # Simulated function to update trading parameters
    new_stoploss = 0.9 * market().sl
    new_takeprofit = 1.1 * market().tp
    market().sl, market().tp = new_stoploss, new_takeprofit
    log_general.info(f"Updated stoploss to {new_stoploss} and takeprofit to {new_takeprofit}.")

# Monitor market volatility
def monitor_market_volatility():
    # Simulated function to monitor market volatility
    volatility = "High"
    log_general.warning(f"Market volatility is currently {volatility}. Exercise caution in trading.")

# Fetch latest news
def fetch_latest_news():
    # Simulated function to fetch latest news
    news = [{"headline": "Market reaches new highs", "source": "Crypto News"}]
    for item in news:
        log_general.info(f"News: {item['headline']} - Source: {item['source']}")

# This starts the trading function on a timer
def start_trading():
    log_general.info("Soltrade has now initialized the trading algorithm.")

    trading_sched = BlockingScheduler()
    trading_sched.add_job(perform_analysis, 'interval', seconds=config().price_update_seconds, max_instances=1)
    trading_sched.start()
    perform_analysis()

# To test or purchase the source code, contact @SolVolSupp_bot on Telegram
