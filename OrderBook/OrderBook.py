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
    usernames = set()

    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        first_names: str,
        last_name: str,
        balance=0,
        portfolio=None,
    ):
        self.client_id = Client.counter
        Client.counter += 1
        Client._all_clients += [self]
        if username in Client.usernames:
            raise ValueError(f"Username {username} is not available")
        self.username = username
        Client.usernames.add(username)
        self.password = password
        self.email = email
        self.first_names = first_names
        self.last_name = last_name

        self.balance = balance
        self.portfolio = portfolio if portfolio is not None else {}

    def __str__(self):
        return f"{self.first_names} {self.last_name} ({self.username})"

    @classmethod
    def get_client_by_id(cls, id):
        try:
            return cls._all_clients[id]
        except:
            return None

    def get_id(self):
        return self.client_id

    def add_stock_to_portfolio(self, stock_id, vol):
        ticker = OrderBook.get_ticker_by_id(stock_id)
        if not ticker:
            raise ValueError("Stock does not exist")

        if not ticker in self.portfolio:
            self.portfolio[ticker] = vol
        else:
            if self.portfolio[ticker] + vol < 0:
                raise ValueError("Insufficient stock in portfolio")
            self.portfolio[ticker] += vol

    def display_portfolio(self):
        res = f"Portfolio of {str(self)}:"
        for ticker in self.portfolio:
            res += f"\n  {ticker}:\t  {self.portfolio[ticker]}"
        return res


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
        self._total_volume = volume  # constant keeping track of total volume
        self.transaction_ids = []  # TODO: implement this

    def __str__(self):
        return f"Order[{self.order_id}]: {self.side,OrderBook.get_ticker_by_id(self.stock_id),self.volume} @ {self.price}"

    @classmethod
    def get_order_by_id(cls, id):
        try:
            return cls._all_orders[id]
        except:
            return None

    def get_id(self):
        return self.order_id

    def get_side(self):
        return self.side

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def get_volume(self):
        return self.volume

    def get_total_volume(self):  # to be used in the edit function
        return self._total_volume

    def set_volume(self, amt):  # to be used in the edit function
        """Sets volume of order and returns the difference in volumes."""
        diff = min(
            amt - self._total_volume, -self.volume
        )  # can't decrease volume by more than itself
        self._total_volume += diff
        self.volume += diff
        return diff

    def execute_volume(self, amt):
        self.volume -= amt
        self.client.add_stock_to_portfolio(self.stock_id, amt)

    def get_client(self):
        return self.client

    def get_stock_id(self):
        return self.stock_id

    def cancel(self):
        self.cancelled = True

    def valid_volume(self):  # TODO: rewrite to use correct price
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
            ticker = OrderBook.get_ticker_by_id(self.stock_id)
            if ticker not in client.portfolio:
                return 0
            max_feasible_volume = client.portfolio[ticker]

        return min(max_feasible_volume, self.volume)


class Transaction:
    counter = 0
    _all_transactions = []

    def __init__(self, bidder, bid_price, asker, ask_price, price, vol, stock_id):
        # TODO: rewrite to fix balance and add stock here, and log transaction
        self.transaction_id = Transaction.counter
        Transaction.counter += 1
        Transaction._all_transactions += [self]
        self.timestamp = datetime.now(timezone.utc)
        self.bidder = bidder
        self.bid_price = bid_price
        self.asker = asker
        self.ask_price = ask_price
        self.price = price
        self.vol = vol
        self.stock_id = stock_id

    def __str__(self):
        return f"TRANSACTION: {str(self.asker)} sold {str(self.bidder)} {self.vol} shares of {OrderBook.get_ticker_by_id(self.stock_id)} @ {self.price}"

    @classmethod
    def from_orders(cls, bid, ask, vol):
        if bid.get_stock_id() != ask.get_stock_id():
            raise ValueError(
                "Both orders must be from the same stock"
            )  # precondition: bid and ask have same stock

        # trade is executed at the price of the earlier order
        price = bid.get_price() if bid.timestamp < ask.timestamp else ask.get_price()

        return cls(
            bid.get_client(),
            bid.get_price(),
            ask.get_client(),
            ask.get_price(),
            price,
            vol,
            bid.get_stock_id(),
        )

    @classmethod
    def get_transaction_by_id(cls, id):
        try:
            return cls._all_transactions[id]
        except:
            return None

    @classmethod
    def export_transactions(cls):
        """Returns all transactions as 5-tuples (order_id, timestamp, price, volume, stock_id) for export to frontend."""
        return [
            (t.transaction_id, t.timestamp, t.price, t.vol, t.stock_id)
            for t in cls._all_transactions
        ]


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
    client1 = Client("tapple", "pw", "timcook@aol.com", "Tim", "Cook")
    client2 = Client(
        "goat", "pw", "lbj@nba.com", "LeBron", "James", balance=1_000_000_000
    )

    order_book = OrderBook("AAPL")
    client1.add_stock_to_portfolio(0, 100)

    order_book.place_order(SELL, 100.5, 10, 0)
    order_book.place_order(BUY, 101.0, 5, 1)
"""


class OrderBook:
    counter = 0
    _all_books = []

    def __init__(self, ticker: str):
        self.stock_id = OrderBook.counter
        OrderBook.counter += 1
        OrderBook._all_books += [self]
        if not ticker:
            ticker = ""
        self.ticker = ticker
        self.bids = SortedList(key=lambda o: (-o.price, o.timestamp))
        self.asks = SortedList(key=lambda o: (o.price, o.timestamp))

    @classmethod
    def get_book_by_id(cls, id):
        try:
            return cls._all_books[id]
        except:
            return None

    @classmethod
    def get_ticker_by_id(cls, id):
        book = cls.get_book_by_id(id)
        if not book:
            return None
        return book.ticker

    def _place_order(self, order):
        """Place a given order and execute trades if feasible."""
        opposite_book = self.asks if order.side == BUY else self.bids
        same_book = self.bids if order.side == BUY else self.asks

        # while a trade is feasible, try to execute one
        while order.valid_volume() > 0 and opposite_book:
            other_order = opposite_book[0]
            trade_price = other_order.get_price()

            # if all trades at valid prices have been executed, no more trades are executable
            if order.side == SELL and trade_price < order.get_price():
                break
            elif order.side == BUY and trade_price > order.get_price():
                break

            # if the other order isn't valid, remove it
            if other_order.valid_volume() == 0:
                print("WARNING: Cancelled " + other_order)
                self._cancel(other_order)
                opposite_book = opposite_book[1:]
                continue

            # otherwise, a positive number of shares can be traded
            trade_volume = min(order.valid_volume(), other_order.valid_volume())

            if order.side == BUY:
                order.execute_volume(trade_volume)
                other_order.execute_volume(-trade_volume)
                trade = Transaction.from_orders(order, other_order, trade_volume)
            else:  # order.side == SELL
                order.execute_volume(-trade_volume)
                other_order.execute_volume(trade_volume)
                trade = Transaction.from_orders(other_order, order, trade_volume)
            print(trade)

            if other_order.volume == 0:
                self._cancel(other_order)

        print(order)
        if order.volume > 0:
            # all possible trades have been executed, so store the remaining order in the book
            same_book.add(order)

    def place_order(self, side, price, volume, client):
        """Place order directly with the information entered."""
        order = Order(self.stock_id, side, price, volume, client)
        self._place_order(order)
        return order.order_id

    def _cancel(self, order):
        """Cancel an order."""
        book = self.bids if order.get_side() == BUY else self.asks

        order.cancel()  # mark order as cancelled (to prevent future executions of it)

        try:
            book.remove(order)
        except:
            return False

        return True

    def cancel(self, order_id):
        """Cancel an order, specified by its id."""
        self._cancel(Order.get_order_by_id(order_id))

    def get_best_bid(self):
        """Returns highest bid price."""
        return self.bids[0].get_price() if self.bids else 0

    def get_best_ask(self):
        """Returns lowest ask price."""
        return self.asks[0].get_price() if self.asks else 0

    def get_best(self):
        """Returns tuple with (highest bid, lowest ask)."""
        return (self.get_best_bid(), self.get_best_ask())

    def get_volume_at_price(self, side, price):
        """Returns volume of open orders (some of which may not be valid) for given side of the order book."""
        book = self.bids if side == BUY else self.asks
        key = (
            (-price, datetime.fromtimestamp(0, timezone.utc))
            if side == BUY
            else (price, datetime.fromtimestamp(0, timezone.utc))
        )

        first_index = book.bisect_key_left(
            key
        )  # first index i s.t. book[i].price >= price
        if book[first_index].get_price() > price:
            return 0

        index = first_index
        volume = 0
        while index < len(book) and book[index].get_price() == price:
            volume += book[index].get_volume()
            index += 1
        return volume

    def edit_order(self, order_id, new_price, new_vol):
        """Edits order with new price and volume. Returns difference in volumes (as it may not be possible to change volume fully)."""
        order = Order.get_order_by_id(order_id)
        order.set_price(new_price)
        diff = order.set_volume(new_vol)
        # TODO: execute orders at this new (price, vol), if possible
        return diff

    def export_asks(self):
        """Returns all asks as 5-tuples (order_id, timestamp, price, volume, stock_id) for export to frontend."""
        return [
            (o.order_id, o.timestamp, o.price, o.volume, o.stock_id) for o in self.asks
        ]

    def get_all_bids(self):
        """Returns all bids as 5-tuples (order_id, timestamp, price, volume, stock_id) for export to frontend."""
        return [
            (o.order_id, o.timestamp, o.price, o.volume, o.stock_id) for o in self.bids
        ]


if __name__ == "__main__":
    client1 = Client("tapple", "pw", "timcook@aol.com", "Tim", "Cook")
    client2 = Client(
        "goat", "pw", "lbj@nba.com", "LeBron", "James", balance=1_000_000_000
    )

    # print(client1.portfolio, client2.portfolio)

    order_book = OrderBook("AAPL")
    client1.add_stock_to_portfolio(0, 100)

    # print(client1.portfolio, client2.portfolio)

    order_book.place_order(SELL, 100.5, 10, 0)
    # print(order_book.get_best())
    order_book.place_order(BUY, 101.0, 5, 1)
    # print(order_book.get_best())

    # print(Order.get_order_by_id(1).volume)
    print(client1.display_portfolio())
    print(client2.display_portfolio())
