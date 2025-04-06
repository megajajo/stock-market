"""
Test for cancel_order - seems to be working as intended
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

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

ob.place_order(SELL, 150, 10, client1.get_id())  # order_id = 0
ob.place_order(BUY, 200, 20, client1.get_id())  # order_id = 1

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())

ob.cancel_order(Order.get_order_by_id(1))

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())


"""
Test for get_best + get_best_bid + get_best_ask - seems to be working as intended
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

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

ob.place_order(SELL, 150, 10, client1.get_id())  # order_id = 0
ob.place_order(SELL, 130, 20, client2.get_id())  # order_id = 1
ob.place_order(SELL, 200, 60, client2.get_id())  # order_id = 1
ob.place_order(SELL, 202, 20, client2.get_id())  # order_id = 1
ob.place_order(SELL, 221, 10, client2.get_id())  # order_id = 1

ob.place_order(BUY, 10, 20, client1.get_id())  # order_id = 1
ob.place_order(BUY, 110, 20, client1.get_id())  # order_id = 1
ob.place_order(BUY, 106, 20, client1.get_id())  # order_id = 1
ob.place_order(BUY, 129, 20, client1.get_id())  # order_id = 1

print(ob.get_best())


"""
Test for edit_order - seems to be working as intended
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

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

ob.place_order(SELL, 150, 10, client1.get_id())  # order_id = 0
ob.place_order(BUY, 200, 30, client1.get_id())  # order_id = 1
order = Order.get_order_by_id(1)
print("Order 1:", order)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())

ob.edit_order(Order.get_order_by_id(1), 300, 15)

print("BUY:", ob.get_all_bids())
print("SELL:", ob.export_asks())

print("Order 1:", order)


"""
Test for get_volume_at_price - seems to be working as intended
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

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

ob.place_order(SELL, 150, 10, client1.get_id())  # order_id = 0
ob.place_order(SELL, 200, 30, client2.get_id())  # order_id = 1
ob.place_order(SELL, 275, 20, client3.get_id())  # order_id = 2
ob.place_order(SELL, 150, 20, client1.get_id())  # order_id = 3

print(ob.get_volume_at_price(BUY, 150))

"""
Test for all "API" functions when the order book is empty - seems to be working as intended
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

client1.portfolio["JPK"] = 500
client2.portfolio["JPK"] = 500

print(ob.get_volume_at_price(SELL, 150))
print(ob.get_best())

print(ob.edit_order(Order.get_order_by_id(0), 200, 10))  # order_id = 0
