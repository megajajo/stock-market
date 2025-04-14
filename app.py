import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from OrderBook.OrderBook import *

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
order_books = [OrderBook("AAPL")]

# Two example users
client1 = Client("tapple", "pw", "timcook@aol.com", "Tim", "Cook", balance=0)
client2 = Client("goat", "pw", "lbj@nba.com", "LeBron", "James", balance=1_000_000_000)
# client1.buy_stock(0, 0, 100)

# print(Client.get_client_by_id(0))
# print(Client.get_client_by_id(1))

# Serve static files from the "static" folder at root ("/")
app.mount("/app", StaticFiles(directory="static", html=True), name="static")

# Redirect root ("/") to the static files
@app.get("/")
async def root():
    return RedirectResponse(url="/app")


# API enpoints
@app.post("/api/place_order")
async def place_order(
    ticker: str, side: str, price: float, volume: int, client_id: int
):
    """
    Place an order for a stock.

    Parameters:
    - ticker: The ticker of the order book.
    - side: The side of the order (buy/sell).
    - price: The price at which to place the order.
    - volume: The number of shares to order.
    - client_id: The ID of the client placing the order.

    Returns:
    - order_id if successful, or an error message.
    """

    print(f"Placing order for stock {ticker}: {side} at {price} for {volume} shares")
    order_side = BUY if side.lower() == "buy" else SELL
    return OrderBook.place_order(ticker, order_side, price, volume, client_id)


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


# Store active WebSocket connections
active_connections = []


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):  # Note: Place some orders before testing this
    await websocket.accept()
    try:
        ticker = await websocket.receive_text()
        print(f"Client subscribed to ticker: {ticker}")
        while True:
            best_bid = OrderBook.get_best_bid(ticker)
            best_ask = OrderBook.get_best_ask(ticker)
            all_bids = OrderBook.get_all_bids(ticker)
            all_asks = OrderBook.get_all_asks(ticker)
            summary = {
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
            }
            encoded = jsonable_encoder(summary)
            await websocket.send_text(json.dumps(encoded))
            await asyncio.sleep(1)  # Updates pushed every second
    except Exception as e:
        print(f"WebSocket error: {e}")
