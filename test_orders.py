from unittest.mock import patch

from bot.orders import place_market, place_limit


# ---------- place_market ----------

@patch("bot.orders.place_order")
def test_place_market_builds_correct_params(mock_place_order):
    mock_place_order.return_value = {"orderId": 1, "status": "FILLED"}

    result = place_market("BTCUSDT", "BUY", 0.01)

    # Assert place_order was called once with the expected params
    mock_place_order.assert_called_once_with({
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.01,
    })
    assert result == {"orderId": 1, "status": "FILLED"}


@patch("bot.orders.place_order")
def test_place_market_returns_client_response_unchanged(mock_place_order):
    mock_response = {"orderId": 42, "status": "FILLED", "executedQty": "0.01"}
    mock_place_order.return_value = mock_response

    result = place_market("ETHUSDT", "SELL", 0.5)

    assert result is mock_response


# ---------- place_limit ----------

@patch("bot.orders.place_order")
def test_place_limit_builds_correct_params(mock_place_order):
    mock_place_order.return_value = {"orderId": 2, "status": "NEW"}

    result = place_limit("BTCUSDT", "SELL", 0.02, 50000)

    mock_place_order.assert_called_once_with({
        "symbol": "BTCUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "quantity": 0.02,
        "price": 50000,
        "timeInForce": "GTC",
    })
    assert result == {"orderId": 2, "status": "NEW"}


@patch("bot.orders.place_order")
def test_place_limit_always_sets_time_in_force_gtc(mock_place_order):
    mock_place_order.return_value = {}

    place_limit("ETHUSDT", "BUY", 1, 3000)

    called_params = mock_place_order.call_args[0][0]
    assert called_params["timeInForce"] == "GTC"


@patch("bot.orders.place_order")
def test_place_market_propagates_exceptions_from_client(mock_place_order):
    mock_place_order.side_effect = RuntimeError("Binance API error: insufficient balance")

    try:
        place_market("BTCUSDT", "BUY", 0.01)
        assert False, "Expected RuntimeError to propagate"
    except RuntimeError as e:
        assert "insufficient balance" in str(e)
