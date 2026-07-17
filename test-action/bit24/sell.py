import os
import hmac
import hashlib
import time
from decimal import Decimal, getcontext

import requests
from dotenv import load_dotenv

# Set decimal precision high enough for small amounts
getcontext().prec = 30

# Load environment variables
load_dotenv()

API_KEY = os.getenv("BIT24_API_KEY")
SECRET_KEY = os.getenv("BIT24_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("BIT24_API_KEY and BIT24_SECRET_KEY must be set in .env file")

BASE_URL = "https://rest.bit24.cash"


def format_amount(amount: float) -> str:
    """
    Convert a float to a decimal string without scientific notation.
    Example: 5.2e-06 -> "0.00000520"
    """
    # Use Decimal to avoid floating point issues and then format
    decimal_value = Decimal(str(amount))
    # Normalize to remove trailing zeros but keep required precision
    # We want at least 8 decimal places for crypto, but we'll just format with 10 and strip trailing zeros
    formatted = f"{decimal_value:.10f}"
    # Remove trailing zeros and decimal point if all zeros after decimal
    formatted = formatted.rstrip('0').rstrip('.')
    if formatted == "":
        formatted = "0"
    return formatted


def generate_signature(params: dict, secret: str) -> str:
    """Generate HMAC-SHA256 signature for Bit24 API."""
    filtered = {k: v for k, v in params.items() if v is not None}
    sorted_items = sorted(filtered.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_items)
    signature = hmac.new(
        secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature


def get_asset(symbol: str) -> dict:
    """Fetch asset information for the given symbol."""
    url = f"{BASE_URL}/asset/capi/v1/wallet/assets"
    headers = {
        "Accept": "application/json",
        "X-BIT24-APIKEY": API_KEY,
    }
    params = {"name": symbol}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise Exception(f"API error: {data.get('error', {}).get('message')}")
    return data["data"]


def get_asset_balance(symbol: str) -> str:
    """Get the balance of a specific asset as a decimal string."""
    data = get_asset(symbol)
    assets = data.get("asset", [])
    if not assets:
        raise ValueError(f"Asset {symbol} not found")
    asset = assets[0]
    balance = asset.get("balance", "0")
    return balance


def check_market(symbol: str, quote: str) -> bool:
    """Check if the market {symbol}/{quote} exists."""
    data = get_asset(symbol)
    assets = data.get("asset", [])
    if not assets:
        return False
    asset = assets[0]
    markets = asset.get("markets", [])
    for m in markets:
        if m.get("base_coin_symbol") == symbol and m.get("quote_coin_symbol") == quote:
            return True
    return False


def submit_order(base_symbol: str, quote_symbol: str, side: int, order_type: int,
                 amount: str, amount_coin_symbol: str = None) -> dict:
    """
    Submit a spot order.
    side: 0 sell, 1 buy
    order_type: 0 Limit, 1 Market, etc.
    amount_coin_symbol: which currency the amount is expressed in.
    """
    url = f"{BASE_URL}/pro/capi/v2/spot-orders/submit"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-BIT24-APIKEY": API_KEY,
    }

    params = {
        "base_coin_symbol": base_symbol,
        "quote_coin_symbol": quote_symbol,
        "side": side,
        "type": order_type,
        "amount": amount,
    }
    if order_type == 1 and amount_coin_symbol:
        params["amount_coin_symbol"] = amount_coin_symbol

    signature = generate_signature(params, SECRET_KEY)
    params["signature"] = signature

    resp = requests.post(url, headers=headers, data=params)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise Exception(f"Order submission failed: {data.get('error', {}).get('message')}")
    return data["data"]


def main():
    # 1. User inputs
    symbol = input("Please Input your Symbol (BTC | ADA | ETH | TRX | ... ) : ").strip().upper()
    quote = input("Please Input your currency (IRT | USDT) : ").strip().upper()
    if quote not in ["IRT", "USDT"]:
        print("Currency must be IRT or USDT.")
        return

    # 2. Check if market exists
    print(f"Checking market {symbol}/{quote}...")
    if not check_market(symbol, quote):
        print(f"Market {symbol}/{quote} does not exist.")
        return
    print("Market exists.")

    # 3. Get current balance of the coin to sell
    try:
        balance_str = get_asset_balance(symbol)
        balance = float(balance_str)
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return

    print(f"Your current {symbol} balance: {balance_str}")

    if balance <= 0:
        print(f"You have no {symbol} to sell.")
        return

    # 4. Ask how much to sell
    sell_input = input(f"How much {symbol} do you want to sell? (enter a number or 'all'): ").strip()
    if sell_input.lower() == "all":
        amount_to_sell = balance
    else:
        try:
            amount_to_sell = float(sell_input)
        except ValueError:
            print("Invalid amount. Please enter a number or 'all'.")
            return
        if amount_to_sell <= 0:
            print("Amount must be positive.")
            return
        if amount_to_sell > balance:
            print(f"You cannot sell more than your balance ({balance_str}).")
            return

    # Format the amount as a decimal string without scientific notation
    amount_str = format_amount(amount_to_sell)

    # 5. Place market sell order
    print(f"Placing market sell order for {amount_str} {symbol}...")
    try:
        result = submit_order(
            base_symbol=symbol,
            quote_symbol=quote,
            side=0,              # sell
            order_type=1,        # market
            amount=amount_str,
            amount_coin_symbol=symbol   # amount is in base coin
        )
        print("Order placed successfully.")
        print(f"Order ID: {result.get('spot_order', {}).get('id')}")
        print(f"Message: {result.get('message')}")

        # 6. Wait 5 seconds for balance update
        print("Waiting 5 seconds for balance update...")
        time.sleep(5)

        # 7. Show updated balance of the quote currency
        quote_balance = get_asset_balance(quote)
        print(f"Updated {quote} balance: {quote_balance}")

    except Exception as e:
        print(f"Error during sell: {e}")


if __name__ == "__main__":
    main()