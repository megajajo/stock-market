import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from TradingBot.TradingBot import TradingBot
from websockets import ConnectionClosedOK
from datetime import datetime, timedelta


@pytest.fixture
def bot():
    with patch("TradingBot.TradingBot.TradingBot.listen_orderbook") as mock_listen:
        mock_listen.return_value = None
        return TradingBot(client_user="test")


@pytest.fixture
def mock_market_data():
    return {"best_bid": 150.0, "best_ask": 151.0, "last_price": 150.5}


@pytest.fixture
def mock_empty_market():
    return {"best_bid": 0, "best_ask": 0, "last_price": 100.0}


def test_initialization(bot):
    assert bot.client_user == "test"
    assert bot.base_size == 50
    assert bot.volatility_window == 20
    assert bot.min_trade_interval == 1
    assert bot.min_spread == 0.01
    assert bot.running == True


def test_volatility_calculation(bot):
    # Empty price history
    assert bot.volatility("AAPL") == 0.1

    # Existing price history
    bot.ticker_states["AAPL"]["price_history"] = [100, 101, 99, 102, 100]
    volatility = bot.volatility("AAPL")
    assert isinstance(volatility, float)
    assert volatility > 0


@pytest.mark.asyncio
async def test_market_make_initialization(bot, mock_empty_market):
    mock_place_order = AsyncMock()
    bot.place_order = mock_place_order

    await bot.market_make("AAPL", mock_empty_market)
    assert mock_place_order.call_count == 2

    # Get the actual call arguments
    calls = mock_place_order.call_args_list
    assert calls[0][0][0] == "AAPL"  # ticker
    assert calls[0][0][1] == "buy"  # side
    assert calls[0][0][3] == bot.base_size  # volume

    assert calls[1][0][0] == "AAPL"  # ticker
    assert calls[1][0][1] == "sell"  # side
    assert calls[1][0][3] == bot.base_size  # volume


@pytest.mark.asyncio
async def test_market_make_normal(bot, mock_market_data):
    # Set up initial state
    bot.ticker_states["AAPL"]["inventory"] = 0
    bot.ticker_states["AAPL"]["last_trade_time"] = datetime.now() - timedelta(seconds=2)

    mock_place_order = AsyncMock()
    bot.place_order = mock_place_order

    await bot.market_make("AAPL", mock_market_data)
    assert mock_place_order.called
    assert mock_place_order.call_count == 2


@pytest.mark.asyncio
async def test_place_order(bot):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        await bot.place_order("AAPL", "buy", 150.0, 50)
        state = bot.ticker_states["AAPL"]
        assert state["inventory"] == 50
        assert len(state["trades"]) == 1
        assert state["trades"][0]["side"] == "buy"
        assert state["trades"][0]["price"] == 150.0
        assert state["trades"][0]["volume"] == 50


def test_handle_shutdown(bot):
    bot.ticker_states["AAPL"]["trades"] = [
        {
            "timestamp": datetime.now(),
            "side": "buy",
            "price": 150.0,
            "volume": 50,
            "pnl": -750,
        }
    ]
    bot.ticker_states["AAPL"]["total_pnl"] = -750
    bot.ticker_states["AAPL"]["inventory"] = 50

    with patch("sys.exit") as mock_exit:
        bot.handle_shutdown()
        mock_exit.assert_called_once_with(0)


def test_log_status(bot):
    bot.ticker_states["AAPL"]["inventory"] = 50
    bot.ticker_states["AAPL"]["total_pnl"] = -750
    bot.ticker_states["AAPL"]["last_price"] = 150.0

    with patch("builtins.print") as mock_print:
        bot.log_status("AAPL")
        assert mock_print.called


@pytest.mark.asyncio
async def test_listen_orderbook(bot):
    msg = '{"AAPL": {"best_bid": 150.0, "best_ask": 151.0, "last_price": 150.5}}'

    mock_ws = AsyncMock()
    mock_ws.__aenter__.return_value = mock_ws
    mock_ws.recv.side_effect = [msg, ConnectionClosedOK(1000, "done")]

    mock_market_make = AsyncMock()
    bot.market_make = mock_market_make

    with patch("websockets.connect", return_value=mock_ws):
        await bot.listen_orderbook()

    mock_market_make.assert_called_once_with(
        "AAPL",
        {"best_bid": 150.0, "best_ask": 151.0, "last_price": 150.5},
    )


if __name__ == "__main__":
    pytest.main(["-v"])
