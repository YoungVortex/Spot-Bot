# Bit24 Trading Bot – Quick Start

A set of Python scripts to interact with the Bit24 cryptocurrency exchange API.  
Includes animated CLI tools for buying, selling, price checking, and API credential management.

## Features
- **Setup & Test** – Store and verify your API keys.
- **Live Price** – Real‑time price tracking with a live dashboard.
- **Buy** – Place a market buy order and see updated balance.
- **Sell** – Place a market sell order and see updated balance.
- **Friendly CLI** – Animated prompts and spinners make it easy to use.

---

## Prerequisites
- Python 3.7+
- `requests`, `python-dotenv`  
  Install with:
  ```bash
  pip install requests python-dotenv
  ```

---

## Installation & Setup

1. **Clone or download** these files into a folder.
2. **Set up your API credentials** using the built‑in tool:
   ```bash
   python setup-token.py
   ```
   This will ask for your **API Key** and **Secret Key** (found in your Bit24 account) and store them in a `.env` file.

3. **Verify your credentials**:
   ```bash
   python use-token.py
   ```
   You should see a success message if the keys are valid.

---

## Script Overview

| Script | Purpose |
|--------|---------|
| `setup-token.py` | Interactive setup of `.env` with API key and secret. |
| `use-token.py`   | Quick test to confirm the API key works. |
| `check-price.py` | Live price display for a given market (updates every 1 second). |
| `buy.py`         | Place a market buy order for a chosen symbol/quote. |
| `sell.py`        | Place a market sell order for a chosen symbol/quote. |

---

## Usage

### 1. Live Price Checker
```bash
python check-price.py
```
You will be prompted for:
- **Symbol** (e.g., `BTC`, `ADA`, `ETH`, `TRX`)
- **Currency** (`IRT` or `USDT`)

The terminal will show a continuously updating dashboard with price, change, request count, and uptime.  
Press `Ctrl+C` to stop.

### 2. Buy Cryptocurrency
```bash
python buy.py
```
Input:
- **Symbol** (e.g., `BTC`)
- **Currency** (`IRT` or `USDT`)
- **Amount** (must be ≥ 50,000 IRT or ≥ 5 USDT)

The script checks the market, submits a market buy order, waits 5 seconds, then displays your updated balance of the purchased asset.

### 3. Sell Cryptocurrency
```bash
python sell.py
```
Input:
- **Symbol** (e.g., `BTC`)
- **Currency** (`IRT` or `USDT`)

After confirming the market exists, the script fetches your current balance of that symbol. You then enter the amount you want to sell (or type `all` to sell everything). A market sell order is placed, and after a short wait, your updated quote currency balance is displayed.

---

## Environment Variables
All scripts read credentials from the `.env` file in the same directory:
```
BIT24_API_KEY=your_api_key
BIT24_SECRET_KEY=your_secret_key
```
Do **not** share this file or commit it to version control.

---

## Notes
- All orders are **market orders** (executed immediately at current price).
- The API endpoints are for **Bit24** (`rest.bit24.cash`).
- Keep your secret key safe – it is used to sign requests.

---

## Troubleshooting
- **“API_KEY and SECRET_KEY must be set”** – run `setup-token.py` again.
- **“Market does not exist”** – double‑check the symbol and currency pair.
- **“Minimum buy”** – respect the minimum amount limits.
- **Network errors** – ensure your internet connection and VPN/proxy settings allow access to Bit24.

---

Enjoy building your trading bot! 🚀