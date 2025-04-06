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
ob.place_order(BUY, 150, 10, client1.get_id())  # order_id = 1

print(ob.get_volume_at_price(SELL, 150))
print(ob.get_best())

print(ob.edit_order(Order.get_order_by_id(0), 200, 10))  # order_id = 0
