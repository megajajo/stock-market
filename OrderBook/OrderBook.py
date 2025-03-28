from enum import Enum
import heapq
from collections import deque
from datetime import datetime, timezone


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
        counter += 1
        self.counter = counter
        all_clients += self
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


class Order:
    counter = 0
    _all_orders = []

    def __init__(self, stock_id, side, price, volume, client_id):
        counter += 1
        self.order_id = counter
        __all_orders += self
        self.timestamp = datetime.now(timezone.utc)
        self.stock_id = stock_id
        self.side = side
        self.price = price
        self.volume = volume
        self.client = Client.get_client_by_id(client_id)

    @staticmethod
    def get_order_by_id(id):
        return Order._all_orders[id]

    def _amount_valid(self):
        """
        Returns the maximum possible volume of a given order that is valid. If 0 is returned,
        then order is not valid.
        """
        client = self.client

        if self.side == BUY:
            max_feasible_volume = client.balance // self.price
        else:  # self.side == SELL
            max_feasible_volume = client.portfolio[self.stock_id]

        return min(max_feasible_volume, self.volume)


class Transaction:
    counter = 0

    def __init__(self, bidder_id, bid_price, asker_id, ask_price, vol, stock_id):
        counter += 1
        self.transaction_id = counter
        self.timestamp = datetime.now(timezone.utc)
        self.bidder_id = bidder_id
        self.bid_price = bid_price
        self.asker_id = asker_id
        self.ask_price = ask_price
        self.vol = vol
        self.stock_id = stock_id


"""
OrderBook Class

This class implements an order book for tracking buy and sell orders in a financial market.
It maintains two priority queues (one for bids and one for asks) and provides methods for
adding, modifying, and removing orders. It also automatically matches trades when possible.

Attributes:
    ticker (str): The symbol representing the asset being traded.
    bids (sorted array): An array storing buy orders, sorted by price (highest first).
    asks (sorted array): An array storing sell orders, sorted by price (lowest first).
    order_map (dict): A mapping of order IDs to their corresponding orders.
    volume_map (dict): A mapping of price and side to volume tradeable at that price.
    queue_map (dict): A mapping of price and side to the relevant queue with orders.

Usage:
    order_book = OrderBook()
    order_book.place_order("order1", BUY, 100.5, 10, "ClientA")
    order_book.place_order("order2", SELL, 101.0, 5, "ClientB")
    best_bid = order_book.get_best_bid()
    best_ask = order_book.get_best_ask()

"""


class OrderBook:
    counter = 0

    def __init__(self, ticker: str):
        counter += 1
        self.counter = counter
        if not ticker:
            ticker = ""
        self.ticker = ticker
        self.bids = []
        self.asks = []
        self.order_map = dict()
        self.volume_map = dict()
        self.queue_map = dict()
        self.cancelled = []

    def __add_order_to_book(self, order):
        """Add order to order book."""
        if not (order.price, order.side) in self.queue_map:
            # orders at price,side don't exist
            self.queue_map[(order.price, order.side)] = deque()
            self.queue_map[(order.price, order.side)].append(order)
            self.volume_map[(order.price, order.side)] = order.volume
            same_book = self.bids if order.side == BUY else self.asks
            heapq.heappush(same_book, order.volume)

        else:
            # orders at price,side already exist
            self.queue_map[(order.price, order.side)].append(order)
            self.volume_map[(order.price, order.side)] += order.volume

    def _place_order(self, order):
        """Place a given order and execute trades if feasible."""
        opposite_book = self.asks if order.side == BUY else self.bids
        same_book = self.bids if order.side == BUY else self.asks
        self.order_map[order.order_id] = order

        while order.volume > 0 and opposite_book:
            trade_price = opposite_book[0]
            opposite_side = order.side.opposite()
            if not trade_price <= order.price:
                break
            try:
                queue = self.queue_map[(trade_price, opposite_side)]
            except:
                break
            other_order = queue[0]
            trade_price = other_order.price, trade_volume = min(
                order.volume, other_order.volume
            )
            other_order.volume -= trade_volume
            order.volume -= trade_volume
            print(
                f"Made by {other_order.client}, taken by {order.client}, {trade_volume} shares @ {trade_price}"
            )

            if other_order.volume == 0:
                self.cancel(other_order.order_id)

        if order.volume > 0:
            # all possible trades have been executed, so store in the book
            self.__add_order_to_book(order)

    def place_order(self, side, price, volume, client):
        """Place order directly with the information entered."""
        self._place_order(Order(side, price, volume, client))
        return

    def cancel(self, order_id):
        """Cancel an order, specified by its id."""
        if order_id in self.order_map:
            order = self.order_map[order_id]
            price_queue = self.queue_map[(order.price, order.side)]
            price_queue.remove(order)

            # if the queue is empty, remove the price from the bids/asks heaps
            if price_queue.len == 0:
                heapq.heappop(same_book)
                same_book = self.bids if order.side == BUY else self.asks

            self.volume_map[(order.price, order.side)] -= order.volume
            self.order_map.delete(order_id)

    def get_best_bid(self):
        """Returns highest bid price."""
        return self.bids[0] if self.bids else None

    def get_best_ask(self):
        """Returns lowest ask price."""
        return self.asks[0] if self.asks else None

    def get_volume_at_price(self, side):
        """Returns volume of open orders for given side of the order book."""
        book = self.bids if side == BUY else self.asks
        if not book:
            return 0
        return book[0]


if __name__ == "__main__":
    order_book = OrderBook("AAPL")
    order_book.place_order("order1", SELL, 100.5, 10, "ClientA")
    order_book.place_order("order2", BUY, 101.0, 5, "ClientB")
    best_bid = order_book.get_best_bid()
    best_ask = order_book.get_best_ask()
    print(best_bid)
