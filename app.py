from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
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
client1 = Client("tapple", "pw", "timcook@aol.com", "Tim", "Cook")
client2 = Client("goat", "pw", "lbj@nba.com", "LeBron", "James", balance=1_000_000_000)
client1.buy_stock(0, 0, 100)


# Serve static files from the "static" folder at root ("/")
app.mount("/app", StaticFiles(directory="static", html=True), name="static")

# Redirect root ("/") to the static files
@app.get("/")
async def root():
    return RedirectResponse(url="/app")


# API enpoints
@app.post("/api/place_order")
async def place_order(
    book_id: int, side: str, price: float, volume: int, client_id: int
):
    """
    Place an order for a stock.

    Parameters:
    - book_id: The ID of the order book.
    - side: The side of the order (buy/sell).
    - price: The price at which to place the order.
    - volume: The number of shares to order.
    - client_id: The ID of the client placing the order.

    Returns:
    - order_id if successful, or an error message.
    """

    print(f"Placing order for stock {book_id}: {side} at {price} for {volume} shares")
    order_book = OrderBook.get_book_by_id(book_id)
    order_side = BUY if side.lower() == "buy" else SELL
    if order_book is None:
        print(OrderBook._all_books)
        return {"error": "Order book not found"}
    return order_book.place_order(order_side, price, volume, client_id)


@app.post("/api/cancel_order")
async def cancel_order(book_id: int, order_id: int):
    """
    Cancel an order for a stock.

    Parameters:
    - book_id: The ID of the order book.
    - order_id: The ID of the order to cancel.

    Returns:
    - success message if successful, or an error message.
    """

    print(f"Cancelling order {order_id} for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}
    order_book.cancel_order(order_id)  # TODO Change to return this
    return "success"


@app.post("/api/edit_order")
async def edit_order(book_id: int, order_id: int, price: float, volume: int):
    """
    Edit an existing order for a stock.

    Parameters:
    - book_id: The ID of the order book.
    - order_id: The ID of the order to edit.
    - price: The new price for the order.
    - volume: The new volume for the order.

    Returns:
    - success message if successful, or an error message.
    """
    print(
        f"Editing order {order_id} for stock {book_id}: new price {price}, new volume {volume}"
    )
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}
    order_book.edit_order(order_id, price, volume)
    return "success"  # TODO Placeholder until we decide what to return


@app.get("/api/get_best_bid")
async def get_best_bid(book_id: int):
    """
    Get the best bid for a stock.

    Parameters:
    - book_id: The ID of the order book.

    Returns:
    - best bid price if successful, or an error message.
    """

    print(f"Getting best bid for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}
    return order_book.get_best_bid()


@app.get("/api/get_best_ask")
async def get_best_ask(book_id: int):
    """
    Get the best ask for a stock.

    Parameters:
    - book_id: The ID of the order book.

    Returns:
    - best ask price if successful, or an error message.
    """

    print(f"Getting best ask for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}
    return order_book.get_best_ask()


@app.get("/api/get_best")
async def get_best(book_id: int):
    """
    Get the best bid and ask for a stock.

    Parameters:
    - book_id: The ID of the order book.

    Returns:
    - best bid and ask prices if successful, or an error message.
    """

    print(f"Getting best bid and ask for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}
    return {
        "best_bid": order_book.get_best_bid(),
        "best_ask": order_book.get_best_ask(),
    }


@app.get("/api/get_volume_at_price")
async def get_volume_at_price(book_id: int, side: str, price: float):
    """
    Get the volume at a specific price for a stock.

    Parameters:
    - book_id: The ID of the order book.
    - price: The price at which to get the volume.

    Returns:
    - volume at the specified price if successful, or an error message.
    """

    print(f"Getting volume at price {price} for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    order_side = BUY if side.lower() == "buy" else SELL
    if order_book is None:
        return {"error": "Order book not found"}
    return order_book.get_volume_at_price(order_side, price)


@app.get("/api/get_all_asks")
async def get_all_asks(book_id: int):
    """
    Get all ask orders for a stock.

    Parameters:
    - book_id: The ID of the order book.

    Returns:
    - list of all ask orders if successful, or an error message.
    """

    print(f"Getting all asks for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}
    print(order_book.get_all_asks())
    return [
        {
            "order_id": order_id,
            "timestamp": timestamp,
            "price": price,
            "volume": volume,
            "stock_id": stock_id,
        }
        for order_id, timestamp, price, volume, stock_id in order_book.get_all_asks()
    ]


@app.get("/api/get_all_bids")
async def get_all_bids(book_id: int):
    """
    Get all bid orders for a stock.

    Parameters:
    - book_id: The ID of the order book.

    Returns:
    - list of all bid orders if successful, or an error message.
    """

    print(f"Getting all bids for stock {book_id}")
    order_book = OrderBook.get_book_by_id(book_id)
    if order_book is None:
        return {"error": "Order book not found"}

    print(order_book.get_all_bids())
    return [
        {
            "order_id": order_id,
            "timestamp": timestamp,
            "price": price,
            "volume": volume,
            "stock_id": stock_id,
        }
        for order_id, timestamp, price, volume, stock_id in order_book.get_all_bids()
    ]


# Store active WebSocket connections
active_connections = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
