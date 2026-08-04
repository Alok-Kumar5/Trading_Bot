import re


def validate_symbol(symbol: str):
    """Symbol must be uppercase letters only, e.g. BTCUSDT."""
    if not re.fullmatch(r"[A-Z]{2,20}", symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Use uppercase letters only, e.g. BTCUSDT"
        )


def validate_side(side: str):
    if side not in ("BUY", "SELL"):
        raise ValueError(f"Side must be BUY or SELL, got '{side}'")


def validate_order_type(order_type: str):
    if order_type not in ("MARKET", "LIMIT"):
        raise ValueError(f"Order type must be MARKET or LIMIT, got '{order_type}'")


def validate_quantity(qty: float):
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0, got {qty}")


def validate_price(price, order_type: str):
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders. Use --price")
        if price <= 0:
            raise ValueError(f"Price must be greater than 0, got {price}")


def validate_all(symbol, side, order_type, qty, price):
    validate_symbol(symbol)
    validate_side(side)
    validate_order_type(order_type)
    validate_quantity(qty)
    validate_price(price, order_type)
