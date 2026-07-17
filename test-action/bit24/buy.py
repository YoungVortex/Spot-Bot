import os
import hmac
import hashlib
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("BIT24_API_KEY")
SECRET_KEY = os.getenv("BIT24_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("API_KEY and SECRET_KEY must be set in .env file")

BASE_URL = "https://rest.bit24.cash"


def generate_signature(params: dict, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for Bit24 API.
    Parameters must be sorted alphabetically and concatenated with '&'.
    """
    # Filter out None values and sort keys
    filtered = {k: v for k, v in params.items() if v is not None}
    sorted_items = sorted(filtered.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_items)
    # Compute HMAC-SHA256 in hex
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
    """Get the balance of a specific asset."""
    data = get_asset(symbol)
    assets = data.get("asset", [])
    if not assets:
        raise ValueError(f"Asset {symbol} not found")
    # The response may contain multiple assets if name matches partially? but we used exact symbol
    asset = assets[0]  # assume first match
    balance = asset.get("balance", "0")
    return balance


def check_market(symbol: str, quote: str) -> bool:
    """
    Check if the market {symbol}/{quote} exists.
    Returns True if exists.
    """
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
    For market order, amount_coin_symbol specifies which currency the amount is in.
    """
    url = f"{BASE_URL}/pro/capi/v2/spot-orders/submit"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-BIT24-APIKEY": API_KEY,
    }

    # Build parameters
    params = {
        "base_coin_symbol": base_symbol,
        "quote_coin_symbol": quote_symbol,
        "side": side,
        "type": order_type,
        "amount": amount,
    }
    # For market orders, we need amount_coin_symbol to indicate amount is in quote currency
    if order_type == 1 and amount_coin_symbol:
        params["amount_coin_symbol"] = amount_coin_symbol
    # Price is not needed for market

    # Generate signature
    signature = generate_signature(params, SECRET_KEY)
    params["signature"] = signature

    # Send POST request with form data
    resp = requests.post(url, headers=headers, data=params)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise Exception(f"Order submission failed: {data.get('error', {}).get('message')}")
    return data["data"]


def main():
    # User input
    symbol = input("Please Input your Symbol (BTC | ADA | ETH | TRX | ... ) : ").strip().upper()
    quote = input("Please Input your currency (IRT | USDT) : ").strip().upper()
    amount_str = input("Please Input How Much You want to buy (min buy is 50000 IRT Or 5 USDT) : ").strip()

    # Validate amount
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return

    if quote == "IRT" and amount < 50000:
        print("Minimum buy for IRT is 50000.")
        return
    elif quote == "USDT" and amount < 5:
        print("Minimum buy for USDT is 5.")
        return
    elif quote not in ["IRT", "USDT"]:
        print("Currency must be IRT or USDT.")
        return

    # Check if market exists
    print(f"Checking market {symbol}/{quote}...")
    if not check_market(symbol, quote):
        print(f"Market {symbol}/{quote} does not exist.")
        return

    print(f"Market exists. Placing market buy order for {amount} {quote} worth of {symbol}...")

    # Place market buy order
    try:
        result = submit_order(
            base_symbol=symbol,
            quote_symbol=quote,
            side=1,          # buy
            order_type=1,    # market
            amount=amount_str,
            amount_coin_symbol=quote
        )
        print("Order placed successfully.")
        print(f"Order ID: {result.get('spot_order', {}).get('id')}")
        print(f"Message: {result.get('message')}")

        # Wait 5 seconds
        print("Waiting 5 seconds for balance update...")
        time.sleep(5)

        # Get updated balance
        balance = get_asset_balance(symbol)
        print(f"Current balance of {symbol}: {balance}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()