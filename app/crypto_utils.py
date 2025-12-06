import base64
import os
import time

import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# Where the seed will be stored inside the container
SEED_PATH = "/data/seed.txt"


def load_private_key(path: str = "student_private.pem"):
    """Load the student's private key from a PEM file."""
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(path: str):
    """Load a public key from a PEM file."""
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP-SHA256.

    Returns a 64-character hex string.
    """
    # 1. Base64 decode
    ciphertext = base64.b64decode(encrypted_seed_b64)

    # 2. RSA/OAEP decrypt with SHA-256 and MGF1(SHA-256)
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # 3. Convert bytes → string
    hex_seed = plaintext.decode("utf-8").strip()

    # 4. Validate: 64-character hex
    if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Invalid hex seed format (must be 64-char lowercase hex)")

    return hex_seed


def save_seed(hex_seed: str, path: str = SEED_PATH):
    """Save the decrypted hex seed to /data/seed.txt (or given path)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(hex_seed)


def load_seed(path: str = SEED_PATH) -> str:
    """Load the hex seed from /data/seed.txt."""
    with open(path, "r") as f:
        return f.read().strip()


def _hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 string,
    as required by TOTP libraries.
    """
    raw_bytes = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(raw_bytes).decode("utf-8")
    return b32


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from hex seed.
    Config:
      - SHA-1 (pyotp default)
      - 30-second period
      - 6 digits
    """
    b32_seed = _hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32_seed, interval=30, digits=6)  # SHA-1 by default
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with ±valid_window periods (±30s if interval=30).
    """
    b32_seed = _hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32_seed, interval=30, digits=6)
    # valid_window=1 → accept previous, current, next time step
    return totp.verify(code, valid_window=valid_window)


def seconds_remaining_in_period(period: int = 30) -> int:
    """
    How many seconds are left in the current TOTP 30s window.
    Used to fill 'valid_for' in /generate-2fa response.
    """
    now = int(time.time())
    return period - (now % period)
