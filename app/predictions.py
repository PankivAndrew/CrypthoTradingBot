import dateutil

from .app import API_KEY, API_SECRET
from crypto_traiding_api.bitmex_run import place_order
import requests
import datetime
import pandas as pd
import numpy as np
import time

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
                normalized_price['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
            close += df['close']
        normalized_price['close'] = close / len(exchange)

    return normalized_price


def EMA_trader(df):
    time_delta = 1  # in minutes (сhoose cryptocurrency and minutes intervsl)

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


def start_trade():
    global rsi_status, ema_status
    while True:
        rsi_df = minute_price_historical('ETC', 'BTC', 10, 1, ['Coinbase'])
        ema_df = minute_price_historical('BTC', 'USD', 30, 1, ['Coinbase'])
        rsi_state = rsi_trader(rsi_df['close'].tolist(), 10)
        ema_state = EMA_trader(ema_df)
        if rsi_state != rsi_status and rsi_state != 'hold':
            rsi_status = rsi_state
            order = place_order(API_KEY, API_SECRET, currency='ETHXBT',
                                action=rsi_state, amount=10)
            print("rsi", order)
            with open('rsi.txt', 'w+') as rsi_f:
                rsi_f.write(rsi_state)
        else:
            rsi_status = 'hold'
            with open('rsi.txt', 'w+') as rsi_f:
                rsi_f.write('hold')
        if ema_state != ema_status and ema_state != 'hold':
            ema_status = ema_state
            order = place_order(API_KEY, API_SECRET, action=ema_state)
            print("ema", order)
            with open('ema.txt', 'w+') as ema_f:
                ema_f.write(ema_state)
        else:
            ema_status = 'hold'
            with open('ema.txt', 'w+') as ema_f:
                ema_f.write('hold')
        # time.sleep(60)
