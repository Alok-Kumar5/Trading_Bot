# Trading Bot — Binance Futures Testnet

A simple Python CLI application to place Market and Limit orders on Binance Futures Testnet (USDT-M).

---

## Project Structure

```
trading_bot/
  bot/
    __init__.py        # package init
    client.py          # Binance API wrapper (HMAC signing + HTTP)
    orders.py          # place_market() and place_limit() logic
    validators.py      # input validation functions
    logging_config.py  # logging setup (file + console)
  cli.py               # interactive CLI entry point (InquirerPy + Rich)
  .env                 # your API keys (never commit this)
  requirements.txt
  logs/
    trading_bot.log    # auto-created on first run
```

---

## Setup Steps

### 1. Get Testnet API Keys
1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in and go to **API Management**
3. Create a new API key and copy the key + secret

### 2. Clone / Download the project
```bash
cd trading_bot
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API keys
```bash
cp .env.example .env
```
Open `.env` and fill in your testnet API key and secret:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

---

## How to Run

From the `trading_bot` directory, start the app:

```bash
python cli.py
```

You get an interactive menu (arrow keys + Enter):

1. **Place a new order** — choose **Market** or **Limit**, then enter:
   - **Symbol** (e.g. `BTCUSDT`)
   - **Side** — **BUY** or **SELL**
   - **Quantity** (e.g. `0.01`; must be greater than 0)
   - **Price** — only for **Limit** orders (USDT, must be greater than 0)
2. **View order history** — enter a symbol to list recent orders for that pair.
3. **Exit** — quit the program.

The CLI shows a short **order summary** (type, symbol, side, qty, price if limit) and asks you to **confirm** before calling Binance. After a successful order, it prints **orderId**, **status**, **executedQty**, and **avgPrice** (or limit **price**) in a table, plus where logs are written.

---

## Example Output

After you confirm an order, the terminal shows Rich-formatted sections similar to:

- **Order summary** — type (MARKET/LIMIT), symbol, current price (if fetched), side, quantity, your limit price and est. total (for limits).
- **Order placed successfully!** — table with **Order ID**, **Status**, **Symbol**, **Side**, **Type**, **Quantity**, **Executed Qty**, and **Filled at** / **Limit price** depending on the response from Binance.

Failures print a clear error message in red; details are also written to `logs/trading_bot.log`.

---

## Validation Rules

| Field    | Rule |
|----------|------|
| symbol   | Uppercase letters only, e.g. BTCUSDT |
| side     | Must be BUY or SELL |
| type     | Must be MARKET or LIMIT |
| qty      | Must be greater than 0 |
| price    | Required for LIMIT orders, must be > 0 |

---

## Log Files

Logs are saved to `logs/trading_bot.log` and also printed to the terminal.

Each log entry captures:
- Timestamp
- Log level (INFO / ERROR)
- Full request params sent to Binance
- Full response received from Binance
- Any errors with details

---

## Assumptions

- Only USDT-M Futures testnet is supported
- `timeInForce` for LIMIT orders is set to `GTC` (Good Till Cancelled)
- Testnet base URL is loaded from `.env` — no code changes needed to switch environments
- Python 3.10+ recommended
