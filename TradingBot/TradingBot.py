import asyncio
import websockets
import json
from OrderBook.OrderBook import *


class TradingBot:
    def __init__(self):
        self.order_book_data = {}
        asyncio.run(self.listen_orderbook())

    async def listen_orderbook(self):
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            await websocket.send("AAPL")
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                print(f"\n Received order book data for ticker {data['ticker']}:")
                print("Best Bid:", data["best_bid"])
                print("Best Ask:", data["best_ask"])
                print("All Bids:")
                for bid in data["all_bids"]:
                    print(
                        f"  [ID: {bid['order_id']}] {bid['price']} x {bid['volume']} @ {bid['timestamp']}"
                    )
                print("All Asks:")
                for ask in data["all_asks"]:
                    print(
                        f"  [ID: {ask['order_id']}] {ask['price']} x {ask['volume']} @ {ask['timestamp']}"
                    )


t = TradingBot()
