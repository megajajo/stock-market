"""
TEST 1

This is the first test

CASE:
- BUY first, but no money
- SELL second, feasible
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
    "Bombini Guzini", "djdiwws", "bombguz@chill.com", "Bombini", "Guzini", 0, None
)  # id = 0
client2 = Client(
    "Trililili Tralila",
    "dfvrecd",
    "trililulu@who.com",
    "Trilili",
    "Tralila",
    1000,
    None,
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
ob.place_order(BUY, 100, 23, client1.get_id())
ob.place_order(SELL, 110, 13, client2.get_id())

printClientInfo(client1)
printClientInfo(client2)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 2
This is the second test

CASE:
- BUY first, but no money
- SELL second, feasible
- prices are compatible

BEHAVIOUR:
- the unfeasible order is eliminated from its list and the other one is added to the list
"""

from OrderBook import *


def printClientInfo(client):
    print(f"Client ID: {client.get_id()}")
    print(client.display_portfolio())
    print(client.display_balance())
    print("\n")


ob = OrderBook("JPK")

client1 = Client(
    "Bombini Guzini", "djdiwws", "bombguz@chill.com", "Bombini", "Guzini", 0, None
)  # id = 0
client2 = Client(
    "Trililili Tralila",
    "dfvrecd",
    "trililulu@who.com",
    "Trilili",
    "Tralila",
    1000,
    None,
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
ob.place_order(BUY, 110, 23, client1.get_id())
ob.place_order(SELL, 100, 13, client2.get_id())

printClientInfo(client1)
printClientInfo(client2)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())
