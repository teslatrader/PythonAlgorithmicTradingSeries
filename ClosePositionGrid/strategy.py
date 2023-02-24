# -*- coding: utf-8 -*-
import config, pprint

class ClosePositionGrid:
    def __init__(self, client):
        self.print = pprint.PrettyPrinter()

        self.client = client

        self.symbol = config.PAIR.upper()
        self.order_amount = config.ORDER_AMOUNT
        self.order_lot_size = 0.0
        self.price_start_percentage = 1 + config.PRICE_START / 100
        self.order_price = 0.0
        self.price_step_percentage = 1 + config.PRICE_STEP / 100
        self.max_orders_qty = config.ORDERS_QTY

        self.price_max_limit = 0.0
        self.lot_size_max_limit = 0.0
        self.min_notional = 0.0
        self.max_orders_qty_allowed = 0
        self.lot_size_step = 0
        self.tick_size = 0.0
        self.price_digits = 0
        self.lot_size_digits = 0
        self.orders_placed = 0

        self.setup_symbol_limits()
        self.get_lot_size_digits()
        self.get_price_digits()
        self.check_limits()

    def setup_symbol_limits(self):
        symbol = self.client.get_symbol_info(self.symbol)
        self.print.pprint(symbol)
        self.price_max_limit = float(symbol['filters'][0]['maxPrice'])
        self.lot_size_max_limit = float(symbol['filters'][1]['maxQty'])
        self.min_notional = float(symbol['filters'][2]['minNotional'])
        self.max_orders_qty_allowed = int(symbol['filters'][7]['maxNumOrders'])
        self.lot_size_step = float(symbol['filters'][1]['stepSize'])
        self.tick_size = float(symbol['filters'][0]['tickSize'])

        print(self.price_max_limit)
        print(self.lot_size_max_limit)
        print(self.min_notional)
        print(self.max_orders_qty_allowed)
        print(self.lot_size_step)
        print(self.tick_size)

    def check_limits(self):
        self.order_amount = self.order_amount if self.order_amount >= self.min_notional else self.min_notional
        self.max_orders_qty = self.max_orders_qty if self.max_orders_qty < self.max_orders_qty_allowed else self.max_orders_qty_allowed
        self.price_max_limit = round(self.price_max_limit, self.price_digits)
        self.lot_size_max_limit = round(self.lot_size_max_limit, self.lot_size_digits)

    def get_lot_size_digits(self):
        lot_size_step = self.lot_size_step
        while lot_size_step < 1:
            self.lot_size_digits += 1
            lot_size_step *= 10
        print(f'Symbol lot size digits is {self.lot_size_digits}')

    def get_price_digits(self):
        price_tick_size = self.tick_size
        while price_tick_size < 1:
            self.price_digits += 1
            price_tick_size *= 10
        print(f'Symbol price digits is {self.price_digits}')

    def get_last_price(self):
        order_book = self.client.get_order_book(symbol=self.symbol)
        # self.print.pprint(order_book)
        self.order_price = float(order_book['bids'][0][0])
        print(f'Current price is {self.order_price}')

    def place_orders(self):
        self.get_last_price()
        self.get_order_price(is_first_order=True)
        while True:
            if not self.order_send():
                break
            self.get_order_price()

    def get_order_price(self, is_first_order=False):
        if is_first_order:
            self.order_price = round(self.order_price * self.price_start_percentage, self.price_digits)
        else:
            self.order_price = round(self.order_price * self.price_step_percentage, self.price_digits)
        self.order_price = self.order_price if self.order_price < self.price_max_limit else self.price_max_limit
        print(f'Limit order price is {self.order_price}')

    def order_send(self):
        self.order_lot_size = round(self.order_amount / self.order_price, self.lot_size_digits)
        self.order_lot_size = self.order_lot_size if self.order_lot_size < self.lot_size_max_limit else self.lot_size_max_limit

        if self.orders_placed < self.max_orders_qty:
            try:
                order = self.client.order_limit_sell(symbol=self.symbol, quantity=self.order_lot_size, price=str(self.order_price))
                self.orders_placed += 1
                print(f'Order is sent. Total number of sent orders is {self.orders_placed}')
                if self.orders_placed >= self.max_orders_qty:
                    print(f'We have placed all orders.')
                    return False
                return True
            except Exception as e:
                print(f'We got exception\n{e}')
                return False
