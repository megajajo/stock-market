import asyncio
import websockets
import json
import requests
import numpy as np
from datetime import datetime
from collections import defaultdict
import sys
import matplotlib.pyplot as plt
import os


class TradingBot:
    def __init__(self, client_user: str = "market_maker"):
        self.client_user = client_user
        self.api_url = "http://localhost:8000/api/place_order"
        self.running = True
        self.ticker_states = defaultdict(
            lambda: {
                "inventory": 0,
                "price_history": [],
                "last_trade_time": datetime.now(),
                "last_price": None,
                "total_pnl": 0,
                "trades": [],
            }
        )
        self.base_size = 50
        self.volatility_window = 20
        self.min_trade_interval = 1  # in seconds
        self.min_spread = 0.01
        try:
            print("Initialising")
            asyncio.run(self.listen_orderbook())
        except KeyboardInterrupt:
            self.handle_shutdown()
        except Exception as e:
            print(f"Error initialising: {e}")
            raise

    def handle_shutdown(self):
        if not self.running:
            return
        self.running = False
        print("FINAL PERFORMANCE SUMMARY:")
        total_pnl = 0
        total_trades = 0

        plt.figure(figsize=(12, 6))

        for ticker, state in self.ticker_states.items():
            if state["trades"]:
                print(f"\n{ticker}:")
                print(f"  PnL: {state['total_pnl']}")
                print(f"  Trades: {len(state['trades'])}")
                print(f"  Final Inventory: {state['inventory']}")
                total_pnl += state["total_pnl"]
                total_trades += len(state["trades"])
                timestamps = [trade["timestamp"] for trade in state["trades"]]
                running_pnl = []
                current_pnl = 0
                for trade in state["trades"]:
                    current_pnl += trade["pnl"]
                    running_pnl.append(current_pnl)
                plt.plot(
                    timestamps, running_pnl, label=ticker, marker="o", markersize=2
                )

        print("\nOverall Performance:")
        print(f"PnL: {total_pnl}")
        print(f"Total Trades: {total_trades}")

        plt.title("Total PnL Over Time")
        plt.xlabel("Time")
        plt.ylabel("Total PnL ($)")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_path = os.path.join(os.path.dirname(__file__), "trading_performance.png")
        plt.savefig(plot_path)
        print(f"\nPlot saved to: {plot_path}")

        sys.exit(0)

    def log_status(self, ticker):
        state = self.ticker_states[ticker]
        print(f"PORTFOLIO FOR {ticker}:")
        print(f"Current Inventory: {state['inventory']} shares")
        print(f"PnL: {state['total_pnl']}")
        print(
            f"Current Position Value: {state['inventory'] * state['last_price'] if state['last_price'] else 0}"
        )
        print("\n")

    async def listen_orderbook(self):
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            while self.running:
                try:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    for ticker, ticker_data in data.items():
                        await self.market_make(ticker, ticker_data)
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue

    def volatility(self, ticker):
        price_history = self.ticker_states[ticker]["price_history"]
        if len(price_history) < self.volatility_window:
            return 0.1
        returns = np.diff(np.log(price_history[-self.volatility_window :]))
        return np.std(returns) * np.sqrt(252)

    async def market_make(self, ticker, data):
        best_bid = data["best_bid"]
        best_ask = data["best_ask"]
        last_price = data["last_price"]
        state = self.ticker_states[ticker]

        if best_bid == 0 and best_ask == 0:
            print(f"\nInitialising market for {ticker}")
            reference = last_price if last_price > 0 else 100.0
            initial_spread = self.min_spread
            bid_price = reference * (1 - initial_spread / 100)
            ask_price = reference * (1 + initial_spread / 100)
            await self.place_order(ticker, "buy", bid_price, self.base_size)
            await self.place_order(ticker, "sell", ask_price, self.base_size)
            print(f"Placed initial orders for {ticker}:")
            print(f"Bid: {bid_price} x {self.base_size}")
            print(f"Ask: {ask_price} x {self.base_size}")
            return

        if best_bid and best_ask:
            mid = (best_bid + best_ask) / 2
            state["price_history"].append(mid)
            state["last_price"] = mid
            volatility = self.volatility(ticker)
            last_trade = (datetime.now() - state["last_trade_time"]).total_seconds()
            if last_trade < self.min_trade_interval:
                return
            spread = max(self.min_spread, volatility * 2)
            bid_price = mid - spread / 2
            ask_price = mid + spread / 2
            if state["inventory"] < self.base_size:
                await self.place_order(ticker, "buy", bid_price, self.base_size)
            if state["inventory"] > -self.base_size:
                await self.place_order(ticker, "sell", ask_price, self.base_size)
            self.log_status(ticker)

    async def place_order(self, ticker, side, price, volume):
        payload = {
            "ticker": ticker,
            "side": side,
            "price": price,
            "volume": volume,
            "client_user": self.client_user,
        }

        def send_request():
            try:
                response = requests.post(self.api_url, json=payload)
                if response.status_code == 200:
                    state = self.ticker_states[ticker]
                    pnl = 0
                    if side == "buy":
                        state["inventory"] += volume
                        pnl = -price * volume
                    else:
                        state["inventory"] -= volume
                        pnl = price * volume
                    state["total_pnl"] += pnl
                    state["last_trade_time"] = datetime.now()
                    state["trades"].append(
                        {
                            "timestamp": datetime.now(),
                            "side": side,
                            "price": price,
                            "volume": volume,
                            "pnl": pnl,
                        }
                    )
                    print(f"\nTRADE PLACED FOR {ticker}:")
                    print(f"Side: {side}")
                    print(f"Price: {price}")
                    print(f"Volume: {volume}")
                    print(f"PnL: {pnl}")
                else:
                    print(f"Failed to place order for {ticker}: {response.text}")
            except Exception as e:
                print(f"Connection error placing order for {ticker}: {e}")

        await asyncio.to_thread(send_request)


if __name__ == "__main__":
    bot = TradingBot()
