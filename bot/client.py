import hashlib
import hmac
import logging
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")
API_KEY  = os.getenv("BINANCE_API_KEY", "")
SECRET   = os.getenv("BINANCE_API_SECRET", "")


def _sign(params: dict) -> dict:
    params["timestamp"] = int(time.time() * 1000)
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    signature = hmac.new(
        SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    params["signature"] = signature
    return params


def get_price(symbol: str) -> float:
    try:
        r = httpx.get(
            f"{BASE_URL}/fapi/v1/ticker/price",
            params={"symbol": symbol},
            timeout=10,
        )
        r.raise_for_status()
        return float(r.json()["price"])
    except Exception as e:
        logger.error(f"Failed to fetch price for {symbol}: {e}")
        return None


def get_open_orders(symbol: str) -> list:
    if not API_KEY or not SECRET:
        raise ValueError("API key/secret not found in .env file.")
    params = {"symbol": symbol}
    signed = _sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    try:
        r = httpx.get(
            f"{BASE_URL}/fapi/v1/openOrders",
            params=signed,
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Failed to fetch open orders: {e}")
        return []


def get_order_history(symbol: str) -> list:
    if not API_KEY or not SECRET:
        raise ValueError("API key/secret not found in .env file.")
    params = {"symbol": symbol, "limit": 10}
    signed = _sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    try:
        r = httpx.get(
            f"{BASE_URL}/fapi/v1/allOrders",
            params=signed,
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return sorted(data, key=lambda x: x["time"], reverse=True)
    except Exception as e:
        logger.error(f"Failed to fetch order history: {e}")
        return []


def place_order(params: dict) -> dict:
    if not API_KEY or not SECRET:
        raise ValueError(
            "API key/secret not found. Make sure your .env file is set up correctly."
        )

    signed_params = _sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}

    logger.info(f"Sending order request: {params}")

    try:
        response = httpx.post(
            f"{BASE_URL}/fapi/v1/order",
            params=signed_params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Order response received: {data}")
        return data

    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        logger.error(f"Binance API error {e.response.status_code}: {error_body}")
        raise RuntimeError(f"Binance API error: {error_body}") from e

    except httpx.TimeoutException:
        logger.error("Request timed out.")
        raise RuntimeError("Request timed out. Check your internet connection.")

    except httpx.RequestError as e:
        logger.error(f"Network error: {e}")
        raise RuntimeError(f"Network error: {e}") from e
