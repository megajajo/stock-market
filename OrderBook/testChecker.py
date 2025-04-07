from .OrderBook import *
from testGenerator import generateTest
import argparse
from datetime import datetime, timezone

"""
After each operation I will output a table with all the information about the clients, followed by the transaction lists from the order book.
This information will be put into a file named after the date and time, utc time zone.
This works as a "debugger".
"""


def write_clients(clients, fileName):
    f = open(
        f"OrderBook/TestLog/{fileName}", "a"
    )  # assume it is run from the stock-market folder

    f.write("Clients:\n")

    for client in clients:
        f.write(f"Client ID: {client.get_id()}, ")
        f.write(client.display_portfolio() + ", ")
        f.write(client.display_balance() + "\n\n")

    f.write("\n" + "--" * 30 + "\n")


def write_list(orderBook, fileName, last_order=None):
    asks = orderBook.export_asks()
    bids = orderBook.get_all_bids()
    f = open(
        f"OrderBook/TestLog/{fileName}", "a"
    )  # assume it is run from the stock-market folder

    if last_order is not None:
        if last_order.side == BuyOrSell.BUY:
            f.write(
                f"Last processed order:    BUY: {last_order.client.get_id()}, {last_order.price} @ {last_order.volume}\n"
            )
        else:
            f.write(
                f"Last processed order:    SELL: {last_order.client.get_id()}, {last_order.price} @ {last_order.volume}\n"
            )

    f.write("Asks:\n")
    for order in asks:
        f.write(f"ID: {order[0]}, Price: {order[2]}, Volume: {order[3]} \n")

    f.write("\n")
    f.write("Bids:\n")
    for order in bids:
        f.write(f"ID: {order[0]}, Price: {order[2]}, Volume: {order[3]} \n")
    f.write("\n")


# What if there is an error while doing this? TODO
def run_OrderBook(clients, orders, tickers):
    timestamp = datetime.now(timezone.utc)
    fileName = str(timestamp) + ".txt"
    ob = OrderBook("JPK")
    write_clients(clients, fileName)
    for order in orders:
        if order.side == BuyOrSell.BUY:
            ob._place_order(BUY, order.price, order.volume, order.client.get_id())

        else:
            ob._place_order(SELL, order.price, order.volume, order.client.get_id())

        write_list(ob, fileName, order)
        write_clients(clients, fileName)


def checkValidity():
    # TODO: implement this function to check the validity of the order book and clients
    pass


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
    parser.add_argument(
        "-nt",
        "--newtest",
        action="store_true",
        help="Generate a new test before simulating the order book",
    )
    args = parser.parse_args()

    if args.newtest:
        # Generate a new test
        clients, orders, tickers = generateTest(
            args.allrandom, args.clients, args.orders, args.tickers
        )
        # else get an existing test from a file -- TODO: implement this

    run_OrderBook(clients, orders, tickers)
