import pytest

from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_all,
)


# ---------- validate_symbol ----------

@pytest.mark.parametrize("symbol", ["BTCUSDT", "ETHUSDT", "AB"])
def test_validate_symbol_accepts_valid_symbols(symbol):
    validate_symbol(symbol)  # should not raise


@pytest.mark.parametrize("symbol", ["btcusdt", "BTC-USDT", "123", "", "A"])
def test_validate_symbol_rejects_invalid_symbols(symbol):
    with pytest.raises(ValueError):
        validate_symbol(symbol)


# ---------- validate_side ----------

@pytest.mark.parametrize("side", ["BUY", "SELL"])
def test_validate_side_accepts_valid_sides(side):
    validate_side(side)


@pytest.mark.parametrize("side", ["buy", "sell", "HOLD", ""])
def test_validate_side_rejects_invalid_sides(side):
    with pytest.raises(ValueError):
        validate_side(side)


# ---------- validate_order_type ----------

@pytest.mark.parametrize("order_type", ["MARKET", "LIMIT"])
def test_validate_order_type_accepts_valid_types(order_type):
    validate_order_type(order_type)


@pytest.mark.parametrize("order_type", ["market", "STOP", ""])
def test_validate_order_type_rejects_invalid_types(order_type):
    with pytest.raises(ValueError):
        validate_order_type(order_type)


# ---------- validate_quantity ----------

@pytest.mark.parametrize("qty", [0.01, 1, 100.5])
def test_validate_quantity_accepts_positive_values(qty):
    validate_quantity(qty)


@pytest.mark.parametrize("qty", [0, -1, -0.01])
def test_validate_quantity_rejects_non_positive_values(qty):
    with pytest.raises(ValueError):
        validate_quantity(qty)


# ---------- validate_price ----------

def test_validate_price_not_required_for_market_orders():
    validate_price(None, "MARKET")  # should not raise even with no price


def test_validate_price_required_for_limit_orders():
    with pytest.raises(ValueError):
        validate_price(None, "LIMIT")


def test_validate_price_rejects_non_positive_for_limit():
    with pytest.raises(ValueError):
        validate_price(0, "LIMIT")
    with pytest.raises(ValueError):
        validate_price(-5, "LIMIT")


def test_validate_price_accepts_positive_for_limit():
    validate_price(50000, "LIMIT")  # should not raise


# ---------- validate_all (integration of the above) ----------

def test_validate_all_passes_for_valid_market_order():
    validate_all("BTCUSDT", "BUY", "MARKET", 0.01, None)


def test_validate_all_passes_for_valid_limit_order():
    validate_all("BTCUSDT", "SELL", "LIMIT", 0.01, 50000)


def test_validate_all_raises_on_first_invalid_field():
    # invalid symbol should fail before other checks run
    with pytest.raises(ValueError, match="Invalid symbol"):
        validate_all("btc", "BUY", "MARKET", 0.01, None)
