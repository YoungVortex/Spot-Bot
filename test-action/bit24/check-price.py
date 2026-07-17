import requests
import time
import sys
import os
import itertools
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BIT24_API_KEY", "").strip()
BASE_URL = "https://rest.bit24.cash"
ENDPOINT = "/pro/capi/v1/markets"
INTERVAL = 1.0
REQUEST_TIMEOUT = 10


def animated_input(prompt_text):
    frames = [">._.<", ">__.__<", ">._.<", ">.__.<"]
    spinner = itertools.cycle(frames)
    sys.stdout.write(prompt_text)
    sys.stdout.flush()
    for _ in range(15):
        sys.stdout.write("\r" + prompt_text + next(spinner) + " ")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + prompt_text + ">._.< : ")
    sys.stdout.flush()
    return input()


BASE_COIN = animated_input("Please Input your Symbol (BTC | ADA | ETH | TRX | ... ) : ").strip().upper()
QUOTE_COIN = animated_input("Please Input your currency (IRT | USDT) : ").strip().upper()


def get_price(session):
    url = f"{BASE_URL}{ENDPOINT}"
    headers = {"Accept": "application/json", "X-BIT24-APIKEY": API_KEY}
    try:
        resp = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            return None
        for m in data["data"]["results"]:
            if m["base_coin_symbol"].upper() == BASE_COIN and m["quote_coin_symbol"].upper() == QUOTE_COIN:
                return float(m["each_price"])
    except Exception:
        return None


def build_display(counter, price, last_price, start_time, spinner_frame):
    elapsed = time.time() - start_time
    mins, secs = divmod(int(elapsed), 60)
    hrs, mins = divmod(mins, 60)

    lines = []
    lines.append(f" {BASE_COIN}/{QUOTE_COIN} LIVE TRACKER ")
    lines.append("")
    lines.append(f"  Price      : {price}" if price else "  Price      : ---")
    if price and last_price:
        change = ((price - last_price) / last_price) * 100
        direction = "\u25b2" if change > 0 else "\u25bc" if change < 0 else "\u2500"
        color = "\033[92m" if change > 0 else "\033[91m" if change < 0 else "\033[90m"
        reset = "\033[0m"
        lines.append(f"  Change     : {color}{direction} {change:+.4f}%{reset}")
    else:
        lines.append("  Change     : \u2500\u2500\u2500")
    lines.append(f"  Requests   : {counter}")
    lines.append(f"  Uptime     : {hrs:02d}:{mins:02d}:{secs:02d}")
    lines.append("")
    # Animated spinner line – gives a dynamic feel
    lines.append(f"  Status     : {spinner_frame}  alive")
    lines.append("")
    lines.append("  Ctrl+C to stop ")
    return lines


def render(lines, width=52):
    top = "\u2554" + "\u2550" * (width - 2) + "\u2557"
    bot = "\u255a" + "\u2550" * (width - 2) + "\u255d"
    output = [top]
    for line in lines:
        # Calculate visible length (ignoring ANSI codes for padding)
        stripped = line.replace("\033[0m", "").replace("\033[92m", "").replace("\033[91m", "").replace("\033[90m", "")
        # Also remove the spinner character's possible length – just an approximation
        pad = width - 4 - len(stripped)
        if pad < 0:
            pad = 0
        output.append("\u2551 " + line + " " * pad + " \u2551")
    output.append(bot)
    return "\n".join(output)


def main():
    if not API_KEY:
        print("BIT24_API_KEY not set in .env")
        return

    session = requests.Session()
    last_price = None
    counter = 0
    start_time = time.time()

    # Animation setup: cycling spinner frames (braille-based, looks great in terminal)
    spinner_frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    spinner_cycle = itertools.cycle(spinner_frames)

    # Initial connection animation
    loading_frames = ["|", "/", "-", "\\"]
    loader = itertools.cycle(loading_frames)
    for _ in range(10):
        sys.stdout.write(f"\r  Connecting to BIT24 {next(loader)}")
        sys.stdout.flush()
        time.sleep(0.1)

    os.system("cls" if os.name == "nt" else "clear")

    while True:
        price = get_price(session)
        counter += 1

        current_spinner = next(spinner_cycle)  # Advance the spinner

        lines = build_display(counter, price, last_price, start_time, current_spinner)
        display = render(lines)

        sys.stdout.write("\033[H")  # Move cursor to home
        sys.stdout.write(display)
        sys.stdout.flush()

        last_price = price if price is not None else last_price
        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\033[0m\n\n  Stopped. Goodbye!\n")