import sys
from datetime import datetime
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from rich.rule import Rule

from bot.logging_config import setup_logging
from bot.validators import validate_symbol, validate_quantity, validate_price
from bot.orders import place_market, place_limit
from bot.client import get_price, get_order_history

setup_logging()
console = Console()


def prompt_symbol():
    while True:
        symbol = inquirer.text(message="Symbol [e.g. BTCUSDT]:").execute()
        symbol = symbol.strip().upper()
        try:
            validate_symbol(symbol)
            return symbol
        except ValueError as e:
            console.print(f"  [red]{e}[/red]")


def prompt_quantity():
    while True:
        raw = inquirer.text(message="Quantity [e.g. 0.01]:").execute()
        try:
            qty = float(raw)
            validate_quantity(qty)
            return qty
        except ValueError as e:
            console.print(f"  [red]{e}[/red]")


def prompt_price(order_type):
    if order_type == "MARKET":
        return None
    while True:
        raw = inquirer.text(message="Price [USDT]:").execute()
        try:
            price = float(raw)
            validate_price(price, order_type)
            return price
        except ValueError as e:
            console.print(f"  [red]{e}[/red]")


def show_current_price(symbol):
    price = get_price(symbol)
    if price:
        console.print(f"\n  Current market price: [bold yellow]{price:,.2f} USDT[/bold yellow]")
    else:
        console.print(f"  [dim]Could not fetch current price.[/dim]")
    return price


def print_order_summary(symbol, side, order_type, qty, price, market_price):
    console.print(Rule())
    console.print("[bold cyan]Order summary[/bold cyan]")
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column(style="dim", width=16)
    t.add_column()
    t.add_row("Type",           order_type)
    t.add_row("Symbol",         symbol)
    t.add_row("Current price",  f"{market_price:,.2f} USDT" if market_price else "N/A")
    t.add_row("Side",           f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]")
    t.add_row("Qty",            f"[bold]{qty} BTC[/bold]")
    if price:
        t.add_row("Your price", f"{price:,.2f} USDT")
        t.add_row("Est. total", f"~{qty * price:,.2f} USDT")
    elif market_price:
        t.add_row("Est. total", f"~{qty * market_price:,.2f} USDT")
    console.print(t)
    console.print(Rule())


def print_order_response(result, order_type):
    console.print(f"\n[bold green]Order placed successfully![/bold green]")
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column(style="dim", width=16)
    t.add_column()

    t.add_row("Order ID",     str(result.get("orderId", "N/A")))
    t.add_row("Status",       f"[yellow]{result.get('status', 'N/A')}[/yellow]")
    t.add_row("Symbol",       result.get("symbol", "N/A"))
    t.add_row("Side",         f"[green]{result.get('side')}[/green]" if result.get("side") == "BUY"
                               else f"[red]{result.get('side')}[/red]")
    t.add_row("Type",         result.get("type", "N/A"))
    t.add_row("Quantity",     str(result.get("origQty", "N/A")))
    t.add_row("Executed Qty", str(result.get("executedQty", "N/A")))

    avg = result.get("avgPrice", "0.00")
    price_val = result.get("price", "0.00")
    if float(avg) > 0:
        t.add_row("Filled at",  f"[bold]{float(avg):,.2f} USDT[/bold]")
    elif float(price_val) > 0:
        t.add_row("Limit price", f"[bold]{float(price_val):,.2f} USDT[/bold]")
    else:
        t.add_row("Price",       "Pending fill")

    console.print(t)
    console.print(f"\n[dim]Logged to logs/trading_bot.log[/dim]")
    console.print(Rule())


def show_order_history():
    symbol = prompt_symbol()
    console.print(f"\n[dim]Fetching order history for {symbol}...[/dim]")
    orders = get_order_history(symbol)

    if not orders:
        console.print("[yellow]No orders found for this symbol.[/yellow]")
        return

    console.print(Rule())
    console.print(f"[bold cyan]Last {len(orders)} orders — {symbol}[/bold cyan]\n")

    t = Table(show_header=True, header_style="bold dim", box=None, padding=(0, 2))
    t.add_column("Order ID",  style="dim")
    t.add_column("Type")
    t.add_column("Side")
    t.add_column("Qty")
    t.add_column("Price")
    t.add_column("Status")
    t.add_column("Time")

    for o in orders:
        side_str = f"[green]{o['side']}[/green]" if o["side"] == "BUY" else f"[red]{o['side']}[/red]"
        price_val = float(o.get("avgPrice") or o.get("price") or 0)
        price_str = f"{price_val:,.2f}" if price_val > 0 else "Market"
        status_color = "green" if o["status"] == "FILLED" else "yellow" if o["status"] == "NEW" else "dim"
        time_str = datetime.fromtimestamp(o["time"] / 1000).strftime("%d %b %H:%M")
        t.add_row(
            str(o["orderId"]),
            o["type"],
            side_str,
            str(o["origQty"]),
            price_str,
            f"[{status_color}]{o['status']}[/{status_color}]",
            time_str,
        )

    console.print(t)
    console.print(Rule())


def main():
    console.print(Rule("[bold cyan]Binance Futures Testnet — Trading Bot[/bold cyan]"))

    while True:
        action = inquirer.select(
            message="What would you like to do?",
            choices=[
                {"name": "Place a new order",   "value": "order"},
                {"name": "View order history",  "value": "history"},
                {"name": "Exit",                "value": "exit"},
            ],
        ).execute()

        if action == "exit":
            console.print("[dim]Goodbye.[/dim]")
            sys.exit(0)

        # --- Order history ---
        if action == "history":
            show_order_history()
            continue

        # --- Place order ---
        console.print(Rule())
        order_type = inquirer.select(
            message="Select order type:",
            choices=[
                {"name": "Market  — fills immediately at best price", "value": "MARKET"},
                {"name": "Limit   — fills at your specified price",   "value": "LIMIT"},
            ],
        ).execute()

        console.print(Rule())
        console.print("[bold cyan]Order details[/bold cyan]")

        symbol       = prompt_symbol()
        market_price = show_current_price(symbol)
        side         = inquirer.select(message="Side [BUY/SELL]:", choices=["BUY", "SELL"]).execute()
        qty          = prompt_quantity()
        price        = prompt_price(order_type)

        print_order_summary(symbol, side, order_type, qty, price, market_price)

        confirmed = inquirer.confirm(message="Confirm order?", default=False).execute()
        if not confirmed:
            console.print("[yellow]Order cancelled.[/yellow]")
            continue

        console.print("\n[dim]Placing order...[/dim]")
        try:
            result = place_market(symbol, side, qty) if order_type == "MARKET" \
                     else place_limit(symbol, side, qty, price)
            print_order_response(result, order_type)

        except RuntimeError as e:
            console.print(f"\n[red]Order failed:[/red] {e}")

        # Ask if they want to do something else
        again = inquirer.confirm(message="Place another order?", default=False).execute()
        if not again:
            console.print("[dim]Goodbye.[/dim]")
            sys.exit(0)


if __name__ == "__main__":
    main()
