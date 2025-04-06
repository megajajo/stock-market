"""
TEST 1

This is the first test

CASE:
- BUY first, not feasible
- BUY second, feasible
- SELL third, feasible
- prices are not compatible between #1 and #3

BEHAVIOUR:
- add all orders to the corresponding list
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
printClientInfo(client3)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500
client3.portfolio["JPK"] = 500

# side, price, volume, client
ob.place_order(
    BUY, 150, 2, client3.get_id()
)  # Tung Tung wants to buy 2 JPK at 150, but has no money
ob.place_order(
    BUY, 100, 13, client2.get_id()
)  # Trilili wants to buy 13 JPK at 100 and has some money
ob.place_order(
    SELL, 200, 23, client1.get_id()
)  # Bombini wants to sell 23 JPK at 200 and has stock

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 2

This is the second test

CASE:
- BUY first, not feasible
- BUY second, feasible
- SELL third, feasible
- prices are compatible between #1 and #3 => #1 is removed from the list
- prices are not compatible between #2 and #3 => #3 is added to the list

BEHAVIOUR:
- #2 and #3 are added to the list
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
printClientInfo(client3)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500
client3.portfolio["JPK"] = 500

# side, price, volume, client
ob.place_order(
    BUY, 500, 2, client3.get_id()
)  # Tung Tung wants to buy 2 JPK at 150, but has no money
ob.place_order(
    BUY, 100, 13, client2.get_id()
)  # Trilili wants to buy 13 JPK at 100 and has some money
ob.place_order(
    SELL, 200, 23, client1.get_id()
)  # Bombini wants to sell 23 JPK at 200 and has stock

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 3

This is the third test

CASE:
- BUY first, not feasible
- BUY second, feasible
- SELL third, feasible
- prices are compatible between #1 and #3 => #1 is removed from the list
- prices are compatible between #2 and #3 => #2 is removed from the list and the rest of #3 is added

BEHAVIOUR:
- #3 added to the list (but with modified volume)
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
printClientInfo(client3)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500
client3.portfolio["JPK"] = 500

# side, price, volume, client
ob.place_order(
    BUY, 500, 2, client3.get_id()
)  # Tung Tung wants to buy 2 JPK at 150, but has no money
ob.place_order(
    BUY, 100, 13, client2.get_id()
)  # Trilili wants to buy 13 JPK at 100 and has some money
ob.place_order(
    SELL, 50, 23, client1.get_id()
)  # Bombini wants to sell 23 JPK at 200 and has stock

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 4

CASE:
- SELL first, not feasible
- SELL second, feasible
- BUY third, feasible
- prices are not compatible between #1 and #3

BEHAVIOUR:
- add all orders to the corresponding list
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
    1000,
    None,
)  # id = 2

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500
client3.portfolio["JPK"] = 0

# side, price, volume, client
ob.place_order(
    SELL, 100, 2, client3.get_id()
)  # Tung Tung wants to sell 2 JPK at 150, but has no stock
ob.place_order(
    SELL, 150, 13, client2.get_id()
)  # Trilili wants to sell 13 JPK at 100 and has some stock
ob.place_order(
    BUY, 50, 23, client1.get_id()
)  # Bombini wants to buy 23 JPK at 200 and has money

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 5

CASE:
- SELL first, not feasible
- SELL second, feasible
- BUY third, feasible
- prices are compatible between #1 and #3 => #1 is removed from the list
- prices are not compatible between #2 and #3 => #3 is added to the list

BEHAVIOUR:
- #2 and #3 are added to the list
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
    1000,
    None,
)  # id = 2

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500
client3.portfolio["JPK"] = 0

# side, price, volume, client
ob.place_order(
    SELL, 100, 2, client3.get_id()
)  # Tung Tung wants to sell 2 JPK at 150, but has no stock
ob.place_order(
    SELL, 150, 13, client2.get_id()
)  # Trilili wants to sell 13 JPK at 100 and has some stock
ob.place_order(
    BUY, 120, 23, client1.get_id()
)  # Bombini wants to buy 23 JPK at 200 and has money

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
TEST 6

CASE:
- SELL first, not feasible
- SELL second, feasible
- BUY third, feasible
- prices are compatible between #1 and #3 => #1 is removed from the list
- prices are compatible between #2 and #3 => #2 is modified and the rest of #3 is added

BEHAVIOUR:
- #2 and #3 added to their corresponding lists (but with modified volume)
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
    1000,
    None,
)  # id = 2

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500
client3.portfolio["JPK"] = 0

# side, price, volume, client
ob.place_order(
    SELL, 100, 2, client3.get_id()
)  # Tung Tung wants to sell 2 JPK at 150, but has no stock
ob.place_order(
    SELL, 150, 13, client2.get_id()
)  # Trilili wants to sell 13 JPK at 100 and has some stock
ob.place_order(
    BUY, 170, 23, client1.get_id()
)  # Bombini wants to buy 23 JPK at 200 and has money

printClientInfo(client1)
printClientInfo(client2)
printClientInfo(client3)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())
