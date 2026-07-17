import os
import hmac
import hashlib
import time
import sys
import itertools
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


# ---------- Animation helpers ----------
def animated_input(prompt_text, frames=[">._.<", ">__.__<", ">._.<", ">.__.<"], cycles=8, delay=0.08):
    """Show a playful blinking prompt, then return user input."""
    spinner = itertools.cycle(frames)
    sys.stdout.write(prompt_text)
    sys.stdout.flush()
    for _ in range(cycles):
        sys.stdout.write("\r" + prompt_text + next(spinner) + " ")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\r" + prompt_text + ">._.< : ")
    sys.stdout.flush()
    return input()


def spinner(text, duration=1.0, frames=None):
    """Display a short spinning loader."""
    if frames is None:
        frames = ["|", "/", "-", "\\"]
    cycle = itertools.cycle(frames)
    end = time.time() + duration
    while time.time() < end:
        sys.stdout.write(f"\r{text} {next(cycle)}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(text) + 4) + "\r")  # clear line


# ---------- Bit24 helpers (unchanged) ----------
def generate_signature(params: dict, secret: str) -> str:
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
    data = get_asset(symbol)
    assets = data.get("asset", [])
    if not assets:
        raise ValueError(f"Asset {symbol} not found")
    asset = assets[0]
    balance = asset.get("balance", "0")
    return balance


def check_market(symbol: str, quote: str) -> bool:
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


# ---------- Main with animations ----------
def main():
    # Animated inputs
    symbol = animated_input(
        "Please Input your Symbol (BTC | ADA | ETH | TRX | ... ) : ",
        frames=[">._.<", ">__.__<", ">._.<", ">.__.<"], cycles=8, delay=0.07
    ).strip().upper()

    quote = animated_input(
        "Please Input your currency (IRT | USDT) : ",
        frames=[">._.<", ">__.__<", ">._.<", ">.__.<"], cycles=8, delay=0.07
    ).strip().upper()

    amount_str = animated_input(
        "Please Input How Much You want to buy (min buy is 50000 IRT Or 5 USDT) : ",
        frames=[">._.<", ">__.__<", ">._.<", ">.__.<"], cycles=8, delay=0.07
    ).strip()

    # Validate amount
    try:
        amount = float(amount_str)
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    if quote == "IRT" and amount < 50000:
        print("❌ Minimum buy for IRT is 50000.")
        return
    elif quote == "USDT" and amount < 5:
        print("❌ Minimum buy for USDT is 5.")
        return
    elif quote not in ["IRT", "USDT"]:
        print("❌ Currency must be IRT or USDT.")
        return

    # Animated market check
    print(f"🔍 Checking market {symbol}/{quote}...")
    spinner("Checking", duration=1.0)   # little spinner while API works
    try:
        market_exists = check_market(symbol, quote)
    except Exception as e:
        print(f"❌ Failed to check market: {e}")
        return

    if not market_exists:
        print(f"❌ Market {symbol}/{quote} does not exist.")
        return

    print(f"✅ Market {symbol}/{quote} exists. Placing market buy order...")

    # Animated order placement
    spinner("Placing order", duration=1.2)
    try:
        result = submit_order(
            base_symbol=symbol,
            quote_symbol=quote,
            side=1,
            order_type=1,
            amount=amount_str,
            amount_coin_symbol=quote
        )
    except Exception as e:
        print(f"❌ Order error: {e}")
        return

    print("\n🎉 Order placed successfully!")
    print(f"   Order ID : {result.get('spot_order', {}).get('id')}")
    print(f"   Message  : {result.get('message')}")

    # Animated wait with countdown
    print("\n⏳ Waiting 5 seconds for balance update...")
    for i in range(5, 0, -1):
        sys.stdout.write(f"\r   {i} seconds remaining... ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 30 + "\r")  # clear line

    # Get balance
    try:
        balance = get_asset_balance(symbol)
    except Exception as e:
        print(f"❌ Could not fetch balance: {e}")
        return
    print(f"💰 Current balance of {symbol}: {balance}")


if __name__ == "__main__":
    main()