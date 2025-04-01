from OrderBook import *
from testGenerator import generateTest
import argparse
from datetime import datetime, timezone

"""
After each operation I will output a table with all the information about the clients, followed by the transaction lists from the order book.
This information will be put into a file named after the date and time, utc time zone.
This works as a "debugger".
"""


def print_clients(clients, fileName):
    f = open(
        f"OrderBook/TestLog/{fileName}", "a"
    )  # assume it is run from the stock-market folder
    f.write("Clients:\n")
    for client in clients:
        f.write(f"ID: {client.get_id()}, Balance: {client.get_balance()}\n")
    f.write("\n")


def print_list(orderBook, fileName):
    asks = orderBook.export_asks()
    bids = orderBook.get_all_bids()
    f = open(
        f"OrderBook/TestLog/{fileName}", "a"
    )  # assume it is run from the stock-market folder
    f.write("Asks:\n")
    for order in asks:
        f.write(f"ID: {order[0]}, Price: {order[2]}, Volume: {order[3]} \n")

    f.write("\n")
    f.write("Bids:\n")
    for order in bids:
        f.write(f"ID: {order[0]}, Price: {order[2]}, Volume: {order[3]} \n")
    f.write("\n")


def run_OrderBook(clients, orders):
    timestamp = datetime.now(timezone.utc)
    fileName = str(timestamp) + ".txt"
    f = open(
        f"OrderBook/TestLog/{fileName}", "a"
    )  # assume it is run from the stock-market folder
    f.write("Clients:\n")

    ob = OrderBook("JPK")
    print_clients(clients, fileName)
    for order in orders:
        if order.side == BuyOrSell.BUY:
            ob.place_order(BUY, order.price, order.volume, order.client.get_id())
            f.write(
                f"Last processed order:    BUY: {order.client.get_id()}, {order.price} @ {order.volume}\n"
            )

        else:
            ob.place_order(SELL, order.price, order.volume, order.client.get_id())
            f.write(
                f"Last processed order:    SELL: {order.client.get_id()}, {order.price} @ {order.volume}\n"
            )

        print_list(ob, fileName)
        print_clients(clients, fileName)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test generator for OrderBook")
    parser.add_argument(
        "-c",
        "--clients",
        type=int,
        default=10,
        help="Number of clients to generate (default: 10)",
    )
    parser.add_argument(
        "-o",
        "--orders",
        type=int,
        default=20,
        help="Number of orders to generate (default: 20)",
    )
    parser.add_argument(
        "-t",
        "--tickers",
        type=int,
        default=1,
        help="Number of generated tickers (default: 1)",
    )
    parser.add_argument(
        "-ar",
        "--allrandom",
        action="store_true",
        help="Generate everything at random, ignoring clients and orders",
    )
    args = parser.parse_args()

    clients, orders = generateTest(
        args.allrandom, args.clients, args.orders, args.tickers
    )
    run_OrderBook(clients, orders)
