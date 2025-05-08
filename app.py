import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from OrderBook.OrderBook import *
from pydantic import BaseModel
from database import Database
import new_user_portfolio as new_user
from datetime import datetime, timezone, timedelta

# Initialize the app
app = FastAPI(title="Stock Market")

# Enable CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize order books
order_books = [OrderBook("AAPL"), OrderBook("Stock1"), OrderBook("Stock2")]

# Two example users
client1 = Client(
    "tapple", "pw", "timcook@aol.com", "Tim", "Cook", balance=1_000_000_000
)
client2 = Client("goat", "pw", "lbj@nba.com", "LeBron", "James", balance=1_000_000_000)

client1.portfolio["AAPL"] = 1000
client2.portfolio["AAPL"] = 1000

# client1.buy_stock(0, 0, 100)

# print(Client.get_client_by_id(0))
# print(Client.get_client_by_id(1))

# Serve static files from the "static" folder at root ("/")
app.mount("/app", StaticFiles(directory="static", html=True), name="static")

# Redirect root ("/") to the static files
@app.get("/")
async def root():
    return RedirectResponse(url="/app")


class PlaceOrderRequest(BaseModel):
    ticker: str
    side: str
    price: float
    volume: int
    client_user: str


# API enpoints
@app.post("/api/place_order")
async def place_order(order: PlaceOrderRequest):
    """
    Place a limit order for a stock.

    Parameters:
    - ticker: The ticker of the order book.
    - side: The side of the order (buy/sell).
    - price: The price at which to place the order.
    - volume: The number of shares to order.
    - client_user: The username of the client placing the order.

    Returns:
    - order_id if successful, or an error message.
    """
    ticker = order.ticker
    side = order.side
    price = order.price
    volume = order.volume
    client = Client.get_client_by_username(order.client_user)

    if client is None:
        raise ValueError(f"Client with username {order.client_user} not found.")

    print(f"Placing order for stock {ticker}: {side} at {price} for {volume} shares")
    order_side = BUY if side.lower() == "buy" else SELL
    return OrderBook.place_order(ticker, order_side, price, volume, client)


class MarketOrderRequest(BaseModel):
    ticker: str
    side: str
    volume: int
    client_user: str


@app.post("/api/market_order")
async def market_order(order: MarketOrderRequest):
    """
    Place a market order for a stock.

    Parameters:
    - ticker: The ticker of the order book.
    - side: The side of the order (buy/sell).
    - volume: The number of shares to order.
    - client_user: The username of the client placing the order.

    Returns:
    - order_id if successful, or an error message.
    """
    ticker = order.ticker
    side = order.side
    volume = order.volume
    client = Client.get_client_by_username(order.client_user)

    if client is None:
        raise ValueError(f"Client with username {order.client_user} not found.")

    print(
        f"Placing order for stock {ticker}: {side} at market price for {volume} shares"
    )
    order_side = BUY if side.lower() == "buy" else SELL
    return OrderBook.market_order(ticker, order_side, volume, client)


@app.post("/api/cancel_order")
async def cancel_order(order_id: int):
    """
    Cancel an order for a stock.

    Parameters:
    - order_id: The ID of the order to cancel.

    Returns:
    - success message if successful, or an error message.
    """

    print(f"Cancelling order {order_id}")
    # print(OrderBook.cancel_order(order_id))
    return OrderBook.cancel_order(order_id)


@app.post("/api/edit_order")
async def edit_order(order_id: int, price: float, volume: int):
    """
    Edit an existing order for a stock.

    Parameters:
    - order_id: The ID of the order to edit.
    - price: The new price for the order.
    - volume: The new volume for the order.

    Returns:
    - success message if successful, or an error message.
    """
    print(f"Editing order {order_id}: new price {price}, new volume {volume}")
    OrderBook.edit_order(order_id, price, volume)
    return "success"  # TODO Placeholder until we decide what to return


@app.get("/api/get_best_bid")
async def get_best_bid(ticker: str):
    """
    Get the best bid for a stock.

    Parameters:
    - ticker: The ticker of the order book.

    Returns:
    - best bid price if successful, or an error message.
    """

    print(f"Getting best bid for stock {ticker}")
    return OrderBook.get_best_bid(ticker)


@app.get("/api/get_best_ask")
async def get_best_ask(ticker: str):
    """
    Get the best ask for a stock.

    Parameters:
    - ticker: The ticker of the order book.

    Returns:
    - best ask price if successful, or an error message.
    """

    print(f"Getting best ask for stock {ticker}")
    return OrderBook.get_best_ask(ticker)


@app.get("/api/get_best")
async def get_best(ticker: str):
    """
    Get the best bid and ask for a stock.

    Parameters:
    - ticker: The ticker of the order book.

    Returns:
    - best bid and ask prices if successful, or an error message.
    """

    print(f"Getting best bid and ask for stock {ticker}")
    best_bid, best_ask = OrderBook.get_best(ticker)
    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
    }


@app.get("/api/get_volume_at_price")
async def get_volume_at_price(ticker: str, side: str, price: float):
    """
    Get the volume at a specific price for a stock.

    Parameters:
    - ticker: The ticker of the order book.
    - price: The price at which to get the volume.

    Returns:
    - volume at the specified price if successful, or an error message.
    """

    print(f"Getting volume at price {price} for stock {ticker}")
    order_side = BUY if side.lower() == "buy" else SELL
    return OrderBook.get_volume_at_price(ticker, order_side, price)


@app.get("/api/get_all_asks")
async def get_all_asks(ticker: str):
    """
    Get all ask orders for a stock.

    Parameters:
    - ticker: The ticker of the order book.

    Returns:
    - list of all ask orders if successful, or an error message.
    """

    print(f"Getting all asks for stock {ticker}")
    all_asks = OrderBook.get_all_asks(ticker)
    print(all_asks)
    return [
        {
            "order_id": order_id,
            "timestamp": timestamp,
            "price": price,
            "volume": volume,
            "stock_id": stock_id,
        }
        for order_id, timestamp, price, volume, stock_id in all_asks
    ]


@app.get("/api/get_all_bids")
async def get_all_bids(ticker: str):
    """
    Get all bid orders for a stock.

    Parameters:
    - ticker: The ticker of the order book.

    Returns:
    - list of all bid orders if successful, or an error message.
    """

    print(f"Getting all bids for stock {ticker}")
    all_bids = OrderBook.get_all_bids(ticker)
    print(all_bids)
    return [
        {
            "order_id": order_id,
            "timestamp": timestamp,
            "price": price,
            "volume": volume,
            "stock_id": stock_id,
        }
        for order_id, timestamp, price, volume, stock_id in all_bids
    ]


@app.get("/api/get_client_by_email")
async def get_client_by_email(email: str):
    """
    Used to get a client from the backend by its email.

    Parameters:
    - email: The email we are looking for.

    Returns:
    - The object of the client if it exists or None otherwise.
    """

    print(f"Getting information for client with email {email}")
    client = Client.get_client_by_email(email)
    print(client)
    return client


class ClientData(BaseModel):
    email: str
    first_name: str
    last_name: str


# need to add a proper username and a proper password.
# need to add stock for every ticker !!!!
@app.post("/api/add_new_client")
async def add_new_client(client_data: ClientData):
    """
    Used to get information of a client based on its email. If it doesn not exist, create a new client

    Parameters:
    - email, first name and last name

    Returns:
    - The object of the client
    """
    queryClient = Client.get_client_by_email(client_data.email)

    if queryClient != None:
        return queryClient
    else:
        if not Database().is_email_taken(client_data.email):
            details = Database().account_from_email(client_data.email)
            stocks = Database().retrieve_stock(details[0])
            dic = {}
            for stock in stocks:
                dic[stock[0]] = stock[2]
            client = Client(
                details[1],
                "pass",
                client_data.email,
                client_data.first_name,
                client_data.last_name,
                Database().retrieve_balance(details[0]),
                dic,
            )
        else:
            client = Client(
                "",
                "pass",
                client_data.email,
                client_data.first_name,
                client_data.last_name,
                new_user.money,
                new_user.stocks,
            )
            id = Database().create_client(
                client_data.email,
                client_data.email,
                new_user.money,
                client_data.first_name,
                client_data.last_name,
            )
            for stock, volume in new_user.stocks.items():
                Database().create_owned_stock(id, stock, volume)
        return client


# Store active WebSocket connections
active_connections = []

# Websocket used to get information about the orderbook once a second
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):  # Note: Place some orders before testing this
    await websocket.accept()
    try:
        tickers = ["AAPL", "Stock1", "Stock2"]
        summary = dict()
        print(f"Client subscribed to order book")
        while True:
            for ticker in tickers:
                best_bid = OrderBook.get_best_bid(ticker)
                best_ask = OrderBook.get_best_ask(ticker)
                all_bids = OrderBook.get_all_bids(ticker)
                all_asks = OrderBook.get_all_asks(ticker)
                last_price = OrderBook.get_last_price(ticker)
                last_timestamp = OrderBook.get_last_timestamp(ticker)
                pnl = OrderBook.calculate_pnl_24h(ticker)
                summary[ticker] = {
                    "ticker": ticker,
                    "best_bid": best_bid,
                    "best_ask": best_ask,
                    "all_bids": [
                        {
                            "order_id": order_id,
                            "timestamp": timestamp,
                            "price": price,
                            "volume": volume,
                            "stock_id": stock_id,
                        }
                        for order_id, timestamp, price, volume, stock_id in all_bids
                    ],
                    "all_asks": [
                        {
                            "order_id": order_id,
                            "timestamp": timestamp,
                            "price": price,
                            "volume": volume,
                            "stock_id": stock_id,
                        }
                        for order_id, timestamp, price, volume, stock_id in all_asks
                    ],
                    "last_price": last_price,
                    "last_timestamp": last_timestamp,
                    "pnl": pnl,
                }
            encoded = jsonable_encoder(summary)
            await websocket.send_text(json.dumps(encoded))
            await asyncio.sleep(1)  # Updates pushed every second
    except Exception as e:
        print(f"OrderBook WebSocket error: {e}")


@app.websocket("/client_info")
async def client_info_websocket(websocket: WebSocket):
    """
    WebSocket endpoint to send client information (balance and portfolio).
    """
    await websocket.accept()
    try:
        # Receive the client's username from the WebSocket
        email = await websocket.receive_text()
        print(f"Client subscribed for information: {email}")

        # Fetch the client object
        client = Client.get_client_by_email(email)
        if not client:
            await websocket.send_text(
                json.dumps({"error": f"Client with email {email} not found"})
            )
            await websocket.close()
            return

        # Periodically send client information
        while True:
            pval = OrderBook.portfolio_value(client)
            pnl = {}
            tickers = ["AAPL", "Stock1", "Stock2"]
            for ticker in tickers:
                pnl[ticker] = OrderBook.calculate_pnl_24h(ticker)
            client_info = {
                "balance": client.balance,
                "portfolio": client.portfolio,
                "portfolioValue": pval,
                "pnlInfo": pnl,
            }
            await websocket.send_text(json.dumps(client_info))
            await asyncio.sleep(1)  # Send updates every second
    except Exception as e:
        print(f"Client Info WebSocket error: {e}")
