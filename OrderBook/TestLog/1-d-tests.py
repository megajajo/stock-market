"""
TEST 1

This is the first test

CASE:
- SELL first, feasible
- BUY second, but no balance
- prices are not compatible

BEHAVIOUR:
- add both orders to the corresponding list
"""
from OrderBook import *


def printClientInfo(client):
    print(f"Client ID: {client.get_id()}")
    print(client.display_portfolio())
    print(client.display_balance())
    print("\n")


ob = OrderBook("JPK")

client1 = Client(
    "Bombini Guzini", "djdiwws", "bombguz@chill.com", "Bombini", "Guzini", 1000, None
)  # id = 0
client2 = Client(
    "Trililili Tralila", "dfvrecd", "trililulu@who.com", "Trilili", "Tralila", 0, None
)  # id = 1
client3 = Client(
    "Tung Tung Tung Tung Sahur",
    "asdasc",
    "tung@sahur.com",
    "Tung Tung",
    "Sahur",
    0,
    None,
)  # id = 2

printClientInfo(client1)
printClientInfo(client2)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

# side, price, volume, client
ob.place_order(SELL, 100, 23, client1.get_id())  # Bombini
ob.place_order(BUY, 110, 13, client2.get_id())  # Trilili

printClientInfo(client1)
printClientInfo(client2)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 2
This is the second test

CASE:
- SELL first, feasible
- BUY second, but no balance
- prices are compatible

BEHAVIOUR:
- both orders are added to their corresponding list
- even though the new order is not feasible, it is added to the list because it might become feasible in the future.
"""

from OrderBook import *


def printClientInfo(client):
    print(f"Client ID: {client.get_id()}")
    print(client.display_portfolio())
    print(client.display_balance())
    print("\n")


ob = OrderBook("JPK")

client1 = Client(
    "Bombini Guzini", "djdiwws", "bombguz@chill.com", "Bombini", "Guzini", 1000, None
)  # id = 0
client2 = Client(
    "Trililili Tralila", "dfvrecd", "trililulu@who.com", "Trilili", "Tralila", 0, None
)  # id = 1
client3 = Client(
    "Tung Tung Tung Tung Sahur",
    "asdasc",
    "tung@sahur.com",
    "Tung Tung",
    "Sahur",
    0,
    None,
)  # id = 2

printClientInfo(client1)
printClientInfo(client2)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

# side, price, volume, client
ob.place_order(SELL, 100, 23, client1.get_id())  # Bombini
ob.place_order(BUY, 110, 13, client2.get_id())  # Trilili

printClientInfo(client1)
printClientInfo(client2)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())
