# -*- coding: utf-8 -*-
from binance.client import Client
from strategy import ClosePositionGrid as cpg
import api_keys as api_keys

client = Client(api_keys.API_KEY, api_keys.API_SECRET)

if __name__ == '__main__':
    strategy = cpg(client)
    strategy.place_orders()
