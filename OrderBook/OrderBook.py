from enum import Enum

# import heapq
# from collections import deque
from datetime import datetime, timezone
from sortedcontainers import SortedList


class BuyOrSell(Enum):
    BUY = "buy"
    SELL = "sell"

    def opposite(self):
        if self == BUY:
            return SELL
        else:
            return BUY


BUY = BuyOrSell.BUY
SELL = BuyOrSell.SELL


class Client:
    counter = 0
    _all_clients = []

    def __init__(self, username, password, email, first_names, last_name):
        self.client_id = Client.counter
        Client.counter += 1
        Client._all_clients += [self]
        self.username = username
        self.password = password
        self.email = email
        self.first_names = first_names
        self.last_name = last_name

        self.balance = 0
        self.portfolio = dict()

    @staticmethod
    def get_client_by_id(id):
        return Client._all_clients[id]

    def get_id(self):
        return self.client_id


class Order:
    counter = 0
    _all_orders = []

    def __init__(self, stock_id, side, price, volume, client_id):
        self.order_id = Order.counter
        Order.counter += 1
        self.cancelled = False
        Order._all_orders += [self]
        self.timestamp = datetime.now(timezone.utc)
        self.stock_id = stock_id
        self.side = side
        self.price = price
        self.volume = volume
        self.client = Client.get_client_by_id(client_id)

    @staticmethod
    def get_order_by_id(id):
        return Order._all_orders[id]

    def get_id(self):
        return self.order_id

    def get_side(self):
        return self.side

    def get_price(self):
        return self.price

    def get_volume(self):
        return self.volume

    def add_volume(self, amt):
        self.volume += amt

    def get_client(self):
        return self.client

    def get_stock_id(self):
        return self.stock_id

    def cancel(self):
        self.cancelled = True

    def valid_volume(self):
        """
        Returns the maximum possible volume of a given order that is valid. If 0 is returned,
        then order is not valid or cancelled.
        """
        if self.cancelled:
            return 0

        client = self.client

        if self.side == BUY:
            max_feasible_volume = client.balance // self.price  # no fractional shares
        else:  # self.side == SELL
            if self.stock_id not in client.portfolio:
                return 0
            max_feasible_volume = client.portfolio[self.stock_id]

        return min(max_feasible_volume, self.volume)


class Transaction:
    counter = 0
    _all_transactions = []

    def __init__(self, bidder_id, bid_price, asker_id, ask_price, vol, stock_id):
        self.transaction_id = Transaction.counter
        Transaction.counter += 1
        _all_transactions += [self]
        self.timestamp = datetime.now(timezone.utc)
        self.bidder_id = bidder_id
        self.bid_price = bid_price
        self.asker_id = asker_id
        self.ask_price = ask_price
        self.vol = vol
        self.stock_id = stock_id

    def __init__(self, bid, ask, vol):  # precondition: bid, ask have same stock
        self.transaction_id = Transaction.counter
        Transaction.counter += 1
        _all_transactions += self
        self.timestamp = datetime.now(timezone.utc)
        self.bidder_id = bid.get_client()
        self.bid_price = bid.get_price()
        self.asker_id = ask.get_client()
        self.ask_price = ask.get_price()
        self.vol = vol
        self.stock_id = bid.get_stock_id()


"""
OrderBook Class

This class implements an order book for tracking buy and sell orders in a financial market.
It maintains two priority queues (one for bids and one for asks) and provides methods for
adding, modifying, and removing orders. It also automatically matches trades when possible.

Attributes:
    ticker (str): The symbol representing the asset being traded.
    bids (SortedList): A SortedList storing buy orders, sorted by price (highest first).
    asks (SortedList): A SortedList storing sell orders, sorted by price (lowest first).

Usage:
    client1 = Client("u1","pw","timcook@aol.com","Tim","Cook")
    client2 = Client("u2","pw","lbj@nba.com","LeBron","James")

    order_book = OrderBook("AAPL")
    order_book.place_order(SELL, 100.5, 10, 0)
    order_book.place_order(BUY, 101.0, 5, 1)
    best_bid = order_book.get_best_bid()
    best_ask = order_book.get_best_ask()

"""


class OrderBook:
    counter = 0

    def __init__(self, ticker: str):
        self.stock_id = OrderBook.counter
        OrderBook.counter += 1
        if not ticker:
            ticker = ""
        self.ticker = ticker
        self.bids = SortedList(key=lambda o: (-o.price, o.timestamp))
        self.asks = SortedList(key=lambda o: (o.price, o.timestamp))

    def _place_order(self, order):
        """Place a given order and execute trades if feasible."""
        opposite_book = self.asks if order.side == BUY else self.bids
        same_book = self.bids if order.side == BUY else self.asks

        while order.valid_volume() > 0 and opposite_book:
            other_order = opposite_book[0]
            trade_price = other_order.get_price()
            if not trade_price <= order.get_price():
                break
            trade_volume = min(order.valid_volume(), other_order.valid_volume())
            other_order.add_volume(-trade_volume)
            order.add_volume(-trade_volume)
            print(
                f"Made by {other_order.client}, taken by {order.client}, {trade_volume} shares @ {trade_price}"
            )
            Transaction(order, other_order, trade_volume)

            if other_order.volume == 0:
                self.cancel(other_order.get_id())

        if order.volume > 0:
            # all possible trades have been executed, so store in the book
            same_book.add(order)

    def place_order(self, side, price, volume, client):
        """Place order directly with the information entered."""
        order = Order(self.stock_id, side, price, volume, client)
        self._place_order(order)
        return order.order_id

    def cancel(self, order_id):
        """Cancel an order, specified by its id."""
        order = Order.get_order_by_id(order_id)
        book = self.bids if order.get_side() == BUY else self.asks

        try:
            book.remove(order)
        except:
            return False

        return True

    def get_best_bid(self):
        """Returns highest bid price."""
        return self.bids[0].get_price() if self.bids else 0

    def get_best_ask(self):
        """Returns lowest ask price."""
        return self.asks[0].get_price() if self.asks else 0

    def get_volume_at_price(self, side, price):
        """Returns volume of open orders for given side of the order book."""
        pass

    def edit_order(self, order_id, new_price, new_vol):
        """Edits order with new price and volume."""
        pass


if __name__ == "__main__":
    client1 = Client("u1", "pw", "timcook@aol.com", "Tim", "Cook")
    client2 = Client("u2", "pw", "lbj@nba.com", "LeBron", "James")

    order_book = OrderBook("AAPL")
    order_book.place_order(SELL, 100.5, 10, 0)
    order_book.place_order(BUY, 101.0, 5, 1)
    best_bid = order_book.get_best_bid()
    best_ask = order_book.get_best_ask()
    print(best_bid, best_ask)
