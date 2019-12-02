#!/usr/bin/env python
from crypto_traiding_api.bitmex.bitmex import bitmex_request


def place_order(api_key, api_secret, action='buy', currency='XBTUSD', amount=1):
    orders_numb = amount if action == 'buy' else -amount
    bitmex_client = bitmex_request(test=True, api_key=api_key, api_secret=api_secret)
    order = bitmex_client.Order.Order_new(symbol=currency, orderQty=orders_numb).result()
    return order
