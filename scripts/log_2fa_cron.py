#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timezone

# --- Ensure /app is on sys.path so we can import app.crypto_utils ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /app/scripts
PARENT_DIR = os.path.dirname(BASE_DIR)                 # /app
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from app.crypto_utils import load_seed, generate_totp_code

SEED_PATH = "/data/seed.txt"


def main():
    # If seed is missing, log a clean error message
    if not os.path.exists(SEED_PATH):
        print("Seed file not found; run /decrypt-seed first", file=sys.stderr)
        return

    try:
        hex_seed = load_seed(SEED_PATH)
        code = generate_totp_code(hex_seed)

        # Current UTC time
        now_utc = datetime.now(timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        # Required format: "YYYY-MM-DD HH:MM:SS 2FA Code: XXXXXX"
        print(f"{timestamp} 2FA Code: {code}")
    except Exception as e:
        print(f"Error generating TOTP: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
