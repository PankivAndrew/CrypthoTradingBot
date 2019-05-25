#!/usr/bin/env python
from crypto_traiding_api.bitmex.bitmex import bitmex


def place_order(api_key, api_secret, action='buy', currency='XBTUSD', amount=1):
    orders_numb = amount if action == 'buy' else -amount
    bitmex_client = bitmex(test=True, api_key=api_key, api_secret=api_secret)
    order = bitmex_client.Order.Order_new(symbol=currency, orderQty=orders_numb).result()
    return order

### get orderbook
# orderbook = bitmex_client.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=20).result()
# print(orderbook)

### get your orders
# orders = bitmex_client.Order.Order_getOrders(symbol='XBTUSD', reverse=True).result()
# print(orders)

### get position
# position = bitmex_client.Position.Position_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()
# print(position)

### place order
# order = bitmex_client.Order.Order_new(symbol='XBTUSD', orderQty=-1).result()
# print(order)

### cancel one order
# canceled_order = bitmex_client.Order.Order_cancel(orderID='13e17152-e9c9-bcd9-a10c-9d3cc52f38a7').result()
# print(canceled_order)

### cancel all orders
