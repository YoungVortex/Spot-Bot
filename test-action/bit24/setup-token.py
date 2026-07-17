#!/usr/bin/env python3
"""
setup_env.py - Prompt for Bit24 API credentials with animated input.
Usage: python setup_env.py
"""

import os
import time
import sys
import itertools

ENV_FILE = ".env"


def animated_input(prompt_text, frames=[">._.<", ">__.__<", ">._.<", ">.__.<"], cycles=10, delay=0.08):
    """Show an animated prompt then return user input."""
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


def animated_getpass(prompt_text, frames=[">._.<", ">__.__<", ">._.<", ">.__.<"], cycles=8, delay=0.08):
    """Show an animated prompt, then securely read input (no echo)."""
    import getpass
    spinner = itertools.cycle(frames)
    sys.stdout.write(prompt_text)
    sys.stdout.flush()
    for _ in range(cycles):
        sys.stdout.write("\r" + prompt_text + next(spinner) + " ")
        sys.stdout.flush()
        time.sleep(delay)
    # Final clean prompt with a simple indicator, then hide input
    sys.stdout.write("\r" + prompt_text + ">._.< : ")
    sys.stdout.flush()
    return getpass.getpass("")  # getpass uses its own prompt, so we passed an empty string


def write_env(api_key, secret_key):
    """Write credentials to .env file with a tiny success animation."""
    content = f"""# Bit24 API credentials
BIT24_API_KEY={api_key}
BIT24_SECRET_KEY={secret_key}
"""
    with open(ENV_FILE, "w") as f:
        f.write(content)

    # Animated success message
    sys.stdout.write("\nSaving")
    for _ in range(3):
        for char in [".", "..", "..."]:
            sys.stdout.write(f"\rSaving{char} ")
            sys.stdout.flush()
            time.sleep(0.2)
    print(f"\r✅ Credentials saved to {ENV_FILE}       ")


def main():
    print("🔑 Bit24 API Credential Setup")
    print("Please enter your API credentials from your Bit24 account.")
    print("You can find them in the API management section of your profile.\n")

    # Animated API key prompt
    api_key = animated_input("Enter your API key (X-BIT24-APIKEY): ").strip()
    while not api_key:
        api_key = animated_input("API key cannot be empty. Enter API key: ").strip()

    # Animated secret key prompt (masked)
    secret_key = animated_getpass("Enter your secret key (used for signing POST requests): ").strip()
    while not secret_key:
        secret_key = animated_getpass("Secret key cannot be empty. Enter secret key: ").strip()

    # Confirm before overwriting existing .env
    if os.path.exists(ENV_FILE):
        overwrite = input(f"{ENV_FILE} already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Aborted.")
            return

    write_env(api_key, secret_key)
    print("\nYou can now load these credentials in your code using python-dotenv or os.getenv.")


if __name__ == "__main__":
    main()