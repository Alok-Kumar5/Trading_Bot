from unittest.mock import patch, MagicMock

import httpx
import pytest

from bot import client


# ---------- _sign ----------

def test_sign_adds_timestamp_and_signature():
    params = {"symbol": "BTCUSDT"}
    signed = client._sign(dict(params))

    assert "timestamp" in signed
    assert "signature" in signed
    assert isinstance(signed["timestamp"], int)
    assert isinstance(signed["signature"], str)
    assert len(signed["signature"]) == 64  # sha256 hex digest length


def test_sign_produces_different_signature_for_different_params():
    signed_a = client._sign({"symbol": "BTCUSDT"})
    signed_b = client._sign({"symbol": "ETHUSDT"})

    assert signed_a["signature"] != signed_b["signature"]


# ---------- get_price ----------

@patch("bot.client.httpx.get")
def test_get_price_returns_float_on_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"price": "65000.50"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    price = client.get_price("BTCUSDT")

    assert price == 65000.50
    assert isinstance(price, float)


@patch("bot.client.httpx.get")
def test_get_price_returns_none_on_request_error(mock_get):
    mock_get.side_effect = httpx.RequestError("network down")

    price = client.get_price("BTCUSDT")

    assert price is None


# ---------- place_order ----------

@patch("bot.client.API_KEY", "fake_key")
@patch("bot.client.SECRET", "fake_secret")
@patch("bot.client.httpx.post")
def test_place_order_returns_response_json_on_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"orderId": 1, "status": "FILLED"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = client.place_order({"symbol": "BTCUSDT", "side": "BUY"})

    assert result == {"orderId": 1, "status": "FILLED"}


def test_place_order_raises_without_api_credentials():
    with patch("bot.client.API_KEY", ""), patch("bot.client.SECRET", ""):
        with pytest.raises(ValueError, match="API key/secret not found"):
            client.place_order({"symbol": "BTCUSDT"})


@patch("bot.client.API_KEY", "fake_key")
@patch("bot.client.SECRET", "fake_secret")
@patch("bot.client.httpx.post")
def test_place_order_raises_runtime_error_on_http_status_error(mock_post):
    request = httpx.Request("POST", "https://testnet.binancefuture.com/fapi/v1/order")
    response = httpx.Response(400, text='{"msg":"insufficient balance"}', request=request)
    mock_post.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=request, response=response
    )

    with pytest.raises(RuntimeError, match="insufficient balance"):
        client.place_order({"symbol": "BTCUSDT"})


@patch("bot.client.API_KEY", "fake_key")
@patch("bot.client.SECRET", "fake_secret")
@patch("bot.client.httpx.post")
def test_place_order_raises_runtime_error_on_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("timed out")

    with pytest.raises(RuntimeError, match="timed out"):
        client.place_order({"symbol": "BTCUSDT"})


# ---------- get_open_orders / get_order_history ----------

def test_get_open_orders_raises_without_credentials():
    with patch("bot.client.API_KEY", ""), patch("bot.client.SECRET", ""):
        with pytest.raises(ValueError):
            client.get_open_orders("BTCUSDT")


@patch("bot.client.API_KEY", "fake_key")
@patch("bot.client.SECRET", "fake_secret")
@patch("bot.client.httpx.get")
def test_get_order_history_sorted_most_recent_first(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"orderId": 1, "time": 1000},
        {"orderId": 2, "time": 3000},
        {"orderId": 3, "time": 2000},
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    history = client.get_order_history("BTCUSDT")

    assert [o["orderId"] for o in history] == [2, 3, 1]
