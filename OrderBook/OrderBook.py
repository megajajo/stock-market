from enum import Enum
from typing import Self

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
    _all_clients: list[Self] = []
    _usernames = set[str]()

    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        first_names: str,
        last_name: str,
        balance: float = 0,
        portfolio: dict[str, float] = None,
    ):
        self.client_id = Client.counter
        Client.counter += 1
        Client._all_clients += [self]
        if username in Client._usernames:
            raise ValueError(f"Username {username} is not available")
        self.username = username
        Client._usernames.add(username)
        self.password = password
        self.email = email
        self.first_names = first_names
        self.last_name = last_name

        self.balance = balance
        self.portfolio = portfolio if portfolio is not None else {}

    def __str__(self):
        return f"{self.first_names} {self.last_name} ({self.username})"

    @classmethod
    def get_client_by_id(cls, id: int):
        try:
            return cls._all_clients[id]
        except:
            return None

    def get_id(self) -> int:
        return self.client_id

    def get_balance(self) -> float:
        return self.balance

    def buy_stock(self, stock_id: int, price: float, vol: int):
        # remove money from balance
        if self.balance < vol * price:
            raise ValueError(f"Buyer {self.username} has insufficient funds")
        self.balance -= price * vol

        # add stock to portfolio
        ticker = OrderBook.get_ticker_by_id(stock_id)
        if not ticker:
            raise ValueError("Stock does not exist")
        if vol <= 0:
            raise ValueError("Must buy a positive amount")

        if not ticker in self.portfolio:
            self.portfolio[ticker] = vol
        else:
            self.portfolio[ticker] += vol

    def sell_stock(self, stock_id: int, price: float, vol: int):
        # add money to balance
        self.balance += price * vol

        # remove stock from portfolio
        ticker = OrderBook.get_ticker_by_id(stock_id)
        if not ticker:
            raise ValueError("Stock does not exist")
        if vol <= 0:
            raise ValueError("Must sell a positive amount")

        if not ticker in self.portfolio:
            raise ValueError(f"Seller {self.username} does not own the stock")
        else:
            if self.portfolio[ticker] < vol:
                raise ValueError(f"Seller {self.username} has insufficient stock")
            self.portfolio[ticker] -= vol
            if self.portfolio[ticker] == 0:  # if stock is no longer held
                del self.portfolio[ticker]  # remove from portfolio

    def display_portfolio(self) -> str:
        res = f"Portfolio of {str(self)}:"
        for ticker in self.portfolio:
            res += f"\n  {ticker}:\t  {self.portfolio[ticker]}"
        return res

    def display_balance(self) -> str:
        return f"Balance of {str(self)}:\t  {self.balance}"


class Order:
    counter = 0
    _all_orders: list[Self] = []

    def __init__(
        self, stock_id: int, side: BuyOrSell, price: float, volume: int, client_id: int
    ):
        self.order_id = Order.counter
        Order.counter += 1
        self.terminated = False
        Order._all_orders += [self]
        self.timestamp = datetime.now(timezone.utc)
        self.stock_id = stock_id
        self.stock: OrderBook = OrderBook.get_book_by_id(stock_id)
        self.ticker: str = self.stock.ticker
        self.side = side
        self.price = price
        self.volume = volume  # this is volume left to trade
        self.client_id = client_id
        self.client: Client = Client.get_client_by_id(client_id)
        self._total_volume = volume  # constant keeping track of total volume
        self.transaction_ids: list[int] = []

    def __str__(self):
        return f"Order[{self.order_id}]: {self.side,OrderBook.get_ticker_by_id(self.stock_id),self.volume} @ {self.price}"

    @classmethod
    def get_order_by_id(cls, id: int) -> Self:
        try:
            return cls._all_orders[id]
        except:
            return None

    def get_id(self) -> int:
        return self.order_id

    def get_side(self) -> BuyOrSell:
        return self.side

    def get_price(self) -> float:
        return self.price

    def set_price(self, price: float):
        self.price = price

    def get_volume(self) -> int:
        return self.volume

    def get_total_volume(self) -> int:  # to be used in the edit function !!! NOT USED
        return self._total_volume

    def set_volume(
        self, amt: int
    ) -> int:  # to be used in the edit function, this sets the total_volume
        """Sets volume of order and returns the difference in volumes."""
        diff = max(
            amt - self._total_volume, -self.volume
        )  # can't decrease volume by more than itself
        self._total_volume += diff
        self.volume += diff
        return diff

    def execute_trade(
        self, transaction_id: int, price: float, vol: int, side: BuyOrSell
    ):
        """Update state to execute trade."""
        if self.volume < vol:
            raise ValueError(
                "Order volume was exceeded"
            )  # precondition: vol <= self.volume

        self.transaction_ids += [transaction_id]
        self.volume -= vol

        stock = OrderBook.get_book_by_id(self.stock_id)
        if side == BUY:
            self.client.buy_stock(self.stock_id, price, vol)
            if self.volume > 0 and self.client.get_balance() == 0:
                stock.cancel_order(
                    self
                )  # cancel the order if buyer has run out of funds
        else:  # side == SELL
            self.client.sell_stock(self.stock_id, price, vol)

            ticker = stock.get_ticker()
            if self.volume > 0 and ticker not in self.client.portfolio:
                stock.cancel_order(self)  # cancel the order if seller ran out of stock

        if self.volume == 0:
            self.terminated = True

    def get_client(self) -> Client:
        return self.client

    def get_stock_id(self) -> int:
        return self.stock_id

    def get_executed_volume(self) -> int:
        return self._total_volume - self.volume

    def terminate(self) -> str:
        """Terminate an order."""
        self.terminated = True

        # log termination
        return f"Order[{self.order_id}] terminated after {self.get_executed_volume()}/{self._total_volume} shares executed"

    def is_executable(self) -> bool:
        """Returns whether order is executable (potentially with volume 0)."""
        if self.terminated:  # order isn't executable if terminated
            return False

        if self.side == SELL:
            ticker = OrderBook.get_ticker_by_id(self.stock_id)
            if ticker in self.client.portfolio:
                return self.client.portfolio[ticker] > 0
            elif not ticker in self.client.portfolio:
                return False

        return True

    def executable_volume(self, price=None) -> int:
        """
        Returns the maximum possible executable volume of a given order. If 0 is returned,
        then order is cancelled or has no executable volume at the price.

        Precondition: If order is a sell, then ticker is in the seller's portfolio.
        """
        if self.terminated:
            return 0

        price = price if price is not None else self.price

        if self.side == BUY:
            max_feasible_volume = (
                self.client.get_balance() // price
            )  # no fractional shares
        else:  # self.side == SELL
            ticker = OrderBook.get_ticker_by_id(self.stock_id)
            if ticker not in self.client.portfolio:
                return 0
            max_feasible_volume = self.client.portfolio[ticker]

        return min(max_feasible_volume, self.volume)


class Transaction:
    counter = 0
    _all_transactions: list[Self] = []

    # object as parameter, NOT IDs
    def __init__(self, bid: Order, ask: Order, vol: int):
        if bid.get_stock_id() != ask.get_stock_id():
            raise ValueError(
                "Both orders must be from the same stock"
            )  # precondition: bid and ask have same stock
        else:
            stock_id = bid.get_stock_id()

        self.transaction_id = Transaction.counter
        Transaction.counter += 1
        Transaction._all_transactions += [self]

        self.timestamp = datetime.now(timezone.utc)
        self.bidder = bid.get_client()
        self.bid_price = bid.get_price()
        self.asker = ask.get_client()
        self.ask_price = ask.get_price()

        # trade is executed at the price of the order with earlier timestamp
        price = bid.get_price() if bid.timestamp < ask.timestamp else ask.get_price()
        self.price = price
        self.vol = vol
        self.stock_id = stock_id

        # update the state of the orders to reflect the transaction
        bid.execute_trade(self.transaction_id, price, vol, BUY)
        ask.execute_trade(self.transaction_id, price, vol, SELL)

        # log transaction
        print(self)

    def __str__(self):
        return f"TRANSACTION: {str(self.asker)} sold {str(self.bidder)} {self.vol} shares of {OrderBook.get_ticker_by_id(self.stock_id)} @ {self.price}"

    @classmethod
    def get_transaction_by_id(cls, id: int) -> Self:
        try:
            return cls._all_transactions[id]
        except:
            return None

    @classmethod
    def get_all_transactions(cls) -> dict[int, tuple[datetime, float, int, int]]:
        """Returns all transactions as a dictionary { transaction_id -> (timestamp, price, volume, stock_id) }."""
        return {
            t.transaction_id: (t.timestamp, t.price, t.volume, t.stock_id)
            for t in cls._all_transactions
        }


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
    _all_books: list[Self] = []
    _tickers: dict[str, Self] = {}

    def __init__(self, ticker: str):
        self.stock_id: int = OrderBook.counter
        OrderBook.counter += 1
        OrderBook._all_books += [self]
        if not ticker:
            ticker = "" + self.stock_id
        self.ticker = ticker
        OrderBook._tickers[ticker] = self
        self.bids = SortedList(key=lambda o: (-o.price, o.timestamp))
        self.asks = SortedList(key=lambda o: (o.price, o.timestamp))

    def get_ticker(self):
        return self.ticker

    @classmethod
    def get_all_books(cls) -> dict:
        """Returns all order books as a dict { stock_id -> ticker }"""
        return {id: cls._all_books[id].ticker for id in range(len(cls._all_books))}

    @classmethod
    def get_book_by_id(cls, id: int) -> Self:
        try:
            return cls._all_books[id]
        except:
            return None

    @classmethod
    def get_ticker_by_id(cls, id: int) -> str:
        book = cls.get_book_by_id(id)
        if not book:
            return None
        return book.ticker

    @classmethod
    def get_book_by_ticker(cls, ticker: str) -> Self:
        if ticker not in cls._tickers:
            raise KeyError(f"Ticker {ticker} not found")

        return cls._tickers[ticker]

    # object as parameter, NOT IDs
    def _add_order(self, order: Order):
        """Add an order to the order book and execute trades if feasible."""
        opposite_book = self.asks if order.side == BUY else self.bids
        same_book = self.bids if order.side == BUY else self.asks

        # while a trade is feasible, try to execute one
        while order.is_executable() and opposite_book:
            other_order = opposite_book[0]
            trade_price = other_order.get_price()

            # if all trades at feasible prices have been executed, no more trades are executable
            if order.side == SELL and trade_price < order.get_price():
                break
            elif order.side == BUY and trade_price > order.get_price():
                break

            # if order is executable, but has 0 volume, no more trades would be currently feasible
            if order.executable_volume(trade_price) == 0:
                break

            # if the other order can't trade at this price, skip it
            if other_order.executable_volume(trade_price) == 0:
                if (
                    not other_order.is_executable()  # THIS DOESNT REMOVE UNFEASIBLE BUY ORDERS, but removes unfeasible sell orders
                ):  # if the other order isn't executable, remove it
                    self._remove_order(other_order, cancelling=True)
                    continue
                elif other_order.side == BUY:
                    self._remove_order(other_order, cancelling=True)
                    continue
                else:  # if we dont remove it, then we would always try to match the same orders
                    break

            # otherwise, a positive number of shares can be traded
            trade_volume = min(
                order.executable_volume(trade_price),
                other_order.executable_volume(trade_price),
            )

            if order.side == BUY:
                trade = Transaction(order, other_order, trade_volume)
            else:  # order.side == SELL
                trade = Transaction(other_order, order, trade_volume)

        # an order is added even though it might not be feasible, but it may become feasible in the future
        # this means we should add "active orders" for each client
        if order.volume > 0:
            # all possible trades have been executed, so store the remaining order in the book
            same_book.add(order)

    # object as parameter, NOT IDs
    def _remove_order(self, order: Order, cancelling=False) -> str:
        """Remove an order from the order book."""

        # remove stock from relevant order book
        book = self.bids if order.side == BUY else self.asks

        """if not order in book:
            raise ValueError("Order must be in book to be removed")

            What if I try to remove an order that is not in the book?
            When I cancel an order before putting it in the book.
        """

        if order in book:
            book.remove(order)

        if cancelling:
            return order.terminate()  # mark order as cancelled
        return "Order removed from book"  # if not cancelling

    def _place_order(
        self, side: BuyOrSell, price: float, volume: int, client: Client
    ) -> int:
        """Place order directly with the information entered."""
        order = Order(self.stock_id, side, price, volume, client)
        self._add_order(order)
        return order.order_id

    @staticmethod
    def place_order(
        ticker: str, side: BuyOrSell, price: float, volume: int, client: int | Client
    ) -> int:
        """Class method to place an order with the ticker."""
        match client:
            case int():
                pass
            case Client():
                client = client.get_id()  # if client is entered, replace with client id
            case _:
                raise TypeError("Client or Client id must be entered")

        stock = OrderBook.get_book_by_ticker(ticker)

        return stock._place_order(side, price, volume, client)

    @staticmethod
    def cancel_order(order_id: int) -> str:
        """Class method to cancel an order with ticker and order id."""

        '''if(order_id > Order.counter):
            return f"Order {order_id} does not exist"'''

        order = Order.get_order_by_id(order_id)
        ticker = order.ticker
        stock = OrderBook.get_book_by_ticker(ticker)

        return stock._remove_order(order, cancelling=True)

    def _get_best_bid(self) -> float:
        """Returns highest bid price."""
        return self.bids[0].get_price() if self.bids else 0

    def _get_best_ask(self) -> float:
        """Returns lowest ask price."""
        return self.asks[0].get_price() if self.asks else 0

    def _get_best(self) -> tuple[float, float]:
        """Returns tuple with (highest bid, lowest ask)."""
        return (self._get_best_bid(), self._get_best_ask())

    @staticmethod
    def get_best_bid(ticker: str) -> float:
        stock = OrderBook.get_book_by_ticker(ticker)
        return stock._get_best_bid()

    @staticmethod
    def get_best_ask(ticker: str) -> float:
        stock = OrderBook.get_book_by_ticker(ticker)
        return stock._get_best_ask()

    @staticmethod
    def get_best(ticker: str) -> tuple[float, float]:
        stock = OrderBook.get_book_by_ticker(ticker)
        return stock._get_best()

    def _get_volume_at_price(self, side: BuyOrSell, price: float) -> int:
        """Returns volume of open orders (some of which may not be executable) for given side of the order book."""
        book = self.bids if side == BUY else self.asks

        index = 0
        volume = 0

        while index < len(book) and book[index].get_price() != price:
            index += 1

        while index < len(book) and book[index].get_price() == price:
            volume += book[index].get_volume()
            index += 1

        return volume

    @staticmethod
    def get_volume_at_price(ticker: str, side: BuyOrSell, price: float) -> int:
        stock = OrderBook.get_book_by_ticker(ticker)
        return stock._get_volume_at_price(side, price)

    # objects as parameter, NOT IDs
    def _edit_order(
        self, order: Order, new_price: float, new_vol: int
    ) -> tuple[int, str]:
        """Edits order with new price and volume. Returns difference in volumes (as it may not be possible to change volume fully)."""

        if order == None:
            return (0, "Order does not exist")

        self._remove_order(
            order, cancelling=False
        )  # and temporarily remove from the order book

        # then update it and add back
        order.set_price(new_price)
        diff = order.set_volume(new_vol)
        self._add_order(order)
        return (diff, "Order edited")  # is this really desired ? @Crroco
        # I think we can have this, maybe it helps when we try to automate the trading, so we actually know how much the new order actually is)
        # I think the only "ambiguity" here is for the following case:
        # first I have an order for 10 shares and 7 of them go through, so I am left with 3s.
        # and know I want to change the order to 2 shares (2 < 7 shares which I already transactioned). I think we can do 3 things here:
        # 1. Just cancel the whole order (which happens now because diff = -volume => volume ends up being 0 => cancel), but the traded shares are not recovered.
        # 2. Try to do the inverse order with volume =  7 - 2 at the same price, so we "technically" lose no money
        # 3. Don't allow the change and throw an error. (this seems pointless, but I still included it)

    @staticmethod
    def edit_order(order_id: int, new_price: float, new_vol: int) -> tuple[int, str]:
        """Edits order identified by order id."""
        order = Order.get_order_by_id(order_id)
        ticker = order.ticker
        stock = OrderBook.get_book_by_ticker(ticker)

        return stock._edit_order(order, new_price, new_vol)

    def _get_all_asks(self) -> list[tuple[int, datetime, float, int, int]]:
        """Returns all asks as a list of 5-tuples (order_id, timestamp, price, volume, stock_id)."""
        return [
            (o.order_id, o.timestamp, o.price, o.volume, o.stock_id) for o in self.asks
        ]

    def _get_all_bids(self) -> list[tuple[int, datetime, float, int, int]]:
        """Returns all bids as a list of 5-tuples (order_id, timestamp, price, volume, stock_id)."""
        return [
            (o.order_id, o.timestamp, o.price, o.volume, o.stock_id) for o in self.bids
        ]

    @staticmethod
    def get_all_asks(ticker: str) -> list[tuple[int, datetime, float, int, int]]:
        """Returns all asks of the stock identified by ticker."""
        stock = OrderBook.get_book_by_ticker(ticker)

        return stock._get_all_asks()

    @staticmethod
    def get_all_bids(ticker: str) -> list[tuple[int, datetime, float, int, int]]:
        """Returns all bids of the stock identified by ticker."""
        stock = OrderBook.get_book_by_ticker(ticker)

        return stock._get_all_bids()


if __name__ == "__main__":
    client1 = Client("tapple", "pw", "timcook@aol.com", "Tim", "Cook")
    client2 = Client(
        "goat", "pw", "lbj@nba.com", "LeBron", "James", balance=1_000_000_000
    )

    # print(client1.portfolio, client2.portfolio)

    order_book = OrderBook("AAPL")
    client1.buy_stock(0, 0, 100)

    # print(client1.portfolio, client2.portfolio)

    order_book.place_order(SELL, 100.5, 10, 0)
    # print(order_book.get_best())
    order_book.place_order(BUY, 101.0, 5, 1)
    # print(order_book.get_best())

    # print(Order.get_order_by_id(1).volume)
    print(client1.display_balance())
    print(client1.display_portfolio())
    print(client2.display_balance())
    print(client2.display_portfolio())
