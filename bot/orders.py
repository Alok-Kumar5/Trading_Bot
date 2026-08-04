import logging

from bot.client import place_order

logger = logging.getLogger(__name__)


def place_market(symbol: str, side: str, quantity: float) -> dict:
    params = {
        "symbol":   symbol,
        "side":     side,
        "type":     "MARKET",
        "quantity": quantity,
    }
    logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
    return place_order(params)


def place_limit(symbol: str, side: str, quantity: float, price: float) -> dict:
    params = {
        "symbol":      symbol,
        "side":        side,
        "type":        "LIMIT",
        "quantity":    quantity,
        "price":       price,
        "timeInForce": "GTC",  # Good Till Cancelled
    }
    logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
    return place_order(params)
