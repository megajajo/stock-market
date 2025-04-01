from OrderBook import *
import random
import string

"""
To keep in mind when generating test cases:
classes from OrderBook.py:
BuyOrSell - just Enum class, used in the side of the order
Client - user + password + email + first name + last name + balance = 0 + portofolio = None
Order - stock_id + side + price + volume + client_id + (total_volume + transaction_ids)
Transaction - bid(Order) + asker(Order) + volume + (stock_id)
OrderBook - ticker

I need to generate:
1. Clients
2. Orders

I need to simulate:
1. Transactions
2. OrderBook

Tests to be considered:
1. get vol@price when there are no orders
2. potential "empty book query" errors
3. execute several orders and check if the orderbook is updated correctly
4. order in which the buyer does not have enough money to buy the stock
"""


def generate_random_string(length=8):
    # Choose from uppercase, lowercase, and digits
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


# Generate a single client with random data
def generateClient():
    user = generate_random_string()
    pw = generate_random_string()
    email = generate_random_string() + "@example.com"
    first_name = generate_random_string()
    last_name = generate_random_string()
    balance = random.randint(0, 10000)  # Random balance between 0 and 10,000
    portfolio = None  # Assuming portfolio is None for simplicity

    return Client(user, pw, email, first_name, last_name, balance, portfolio)


# Generate all the clients
def generateClients(num_clients):
    clients = []
    for _ in range(num_clients):
        clients.append(generateClient())
    return clients


def generateOrder(num_tickers, num_clients):
    # side, price , volume, client

    stock_id = 0  # random.randint(0, num_tickers - 1)  # Random stock ID between 0 and the number of tickers
    side = random.choice(
        [BuyOrSell.BUY, BuyOrSell.SELL]
    )  # Randomly choose between BUY and SELL
    client_id = random.randint(
        0, num_clients - 1
    )  # Random client ID between 0 and the number of clients

    # !!!! come back to ensure that these are feasible values
    price = random.randint(1, 1000)  # Random price between 1 and 1000
    volume = random.randint(1, 100)  # Random volume between 1 and 100
    return Order(stock_id, side, price, volume, client_id)


def generateOrders(num_orders, num_tickers, num_clients):
    orders = []
    for _ in range(num_orders):
        orders.append(generateOrder(num_tickers, num_clients))
    return orders


def generateTest(all_random=False, num_clients=10, num_orders=20, num_tickers=1):
    if all_random:
        num_clients = random.randint(1, 100)
        num_orders = random.randint(1, 100)
        num_tickers = random.randint(1, 10)
    else:
        clients = generateClients(num_clients)
        orders = generateOrders(num_orders, num_tickers, num_clients)

    return clients, orders
