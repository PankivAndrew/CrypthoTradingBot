import dateutil
import json

from .app import API_KEY, API_SECRET
from crypto_traiding_api.bitmex_run import place_order
import requests
import datetime
import pandas as pd
import numpy as np
import time
from crypto_traiding_api.bitmex.bitmex import bitmex_request

rsi_status = 'hold'
ema_status = 'hold'


def minute_price_historical(symbol, comparison_symbol, limit, aggregate, exchange=''):
    url = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&limit={}&aggregate={}' \
        .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)
    normalized_price = pd.DataFrame(columns=['timestamp', 'close'])
    close = [0] * (limit + 1)

    if exchange:
        for el in exchange:
            url += '&e={}'.format(el)
            page = requests.get(url)
            url = url.replace('&e={}'.format(el), "")
            data = page.json()['Data']
            df = pd.DataFrame(data)

            if el == 'Coinbase':
                normalized_price['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in
                                                 df.time]
            close += df['close']
        normalized_price['close'] = close / len(exchange)

    return normalized_price


def EMA_trader(df):
    short_rolling = df['close'].rolling(window=10).mean()
    short_rolling.head()

    ema_short = df['close'].ewm(span=20, adjust=False).mean()

    dec_data = ema_short - df.close

    print("ema value", dec_data.values[-1])
    if dec_data.values[-1] > 0:
        decision = "sell"
    elif round(dec_data.values[-1]) == 0:
        decision = "hold"
    else:
        decision = "buy"

    print('ema decision', decision)
    return decision


def conv_for_server(dataframe):
    lst = []
    for el in dataframe.values:
        dic = {'x': dateutil.parser.parse(str(el[0])).timestamp() * 1000, 'y': el[1]}
        lst.append(dic)
    return lst


def rsi_trader(prices, n):
    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = 100. - 100. / (1. + rs)
    print("rsi value: ", rsi)
    if 15 < rsi < 30:
        return "buy"
    elif 70 < rsi < 85:
        return "sell"
    else:
        return "hold"


def start_trade(algorithm_type='rsi', test_duration=60, delay=30):
    global rsi_status, ema_status
    time_spent = 0
    while time_spent < test_duration:
        if algorithm_type == 'rsi':
            algorithm_df = minute_price_historical('ETC', 'USD', 10, 1, ['Coinbase'])
            rsi_state = rsi_trader(algorithm_df['close'].tolist(), 10)

            if rsi_state != rsi_status and rsi_state != 'hold':
                order = place_order(API_KEY, API_SECRET, currency='ETHXBT',
                                    action=rsi_state, amount=10)
                print("rsi", order)
                with open('rsi.txt', 'w+') as rsi_f:
                    rsi_f.write(rsi_state)
                rsi_status = rsi_state
            else:
                rsi_status = 'hold'
                with open('rsi.txt', 'w+') as rsi_f:
                    rsi_f.write(rsi_status)
        else:
            algorithm_df = minute_price_historical('BTC', 'USD', 10, 1, ['Coinbase'])
            ema_state = EMA_trader(algorithm_df)

            if ema_state != ema_status and ema_state != 'hold':
                ema_status = ema_state
                order = place_order(API_KEY, API_SECRET, action=ema_state)
                print("ema", order)
                with open('ema.txt', 'w+') as ema_f:
                    ema_f.write(ema_state)
            else:
                ema_status = 'hold'
                with open('ema.txt', 'w+') as ema_f:
                    ema_f.write(ema_status)
        time.sleep(delay)
        time_spent += delay


def test_algorithms(test_duration=10):
    # global rsi_status, ema_status
    usd_balance_before_rsi = check_our_usd_balance('ETC')
    start_trade('rsi', test_duration, delay=10)
    usd_balance_after_rsi = check_our_usd_balance('ETC')
    rsi_result = usd_balance_before_rsi - usd_balance_after_rsi
    print('USD earnings after RSI: {}'.format(rsi_result))

    usd_balance_before_ema = check_our_usd_balance('BTC')
    start_trade('ema', test_duration, delay=10)
    usd_balance_after_ema = check_our_usd_balance('BTC')
    ema_result = usd_balance_before_ema - usd_balance_after_ema
    print('USD earnings after RSI: {}'.format(ema_result))

    return rsi_result, ema_result


def check_our_usd_balance(currency):
    crypto_currency_exchange_rate = minute_price_historical(currency, 'USD', 10, 1, ['Coinbase'])['close'].iloc[0]
    bitmex_client = bitmex_request(test=True, api_key=API_KEY, api_secret=API_SECRET)
    current_balance = bitmex_client.User.User_getMargin().result()[0]['walletBalance']
    return crypto_currency_exchange_rate * current_balance
