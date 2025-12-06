from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

from app.crypto_utils import (
    load_private_key,
    decrypt_seed,
    save_seed,
    load_seed,
    generate_totp_code,
    verify_totp_code,
    seconds_remaining_in_period,
)

app = FastAPI()


# ---------- Request models ----------

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyCodeRequest(BaseModel):
    code: str | None = None


# ---------- Endpoints ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    """
    POST /decrypt-seed
    - Accepts: { "encrypted_seed": "BASE64..." }
    - Decrypts using student_private.pem
    - Saves hex seed to /data/seed.txt
    - On success: 200 { "status": "ok" }
    - On failure: 500 { "error": "Decryption failed" }
    """
    try:
        # Load private key from file in current working directory
        private_key = load_private_key("student_private.pem")

        # Decrypt to 64-char hex string
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)

        # Save to persistent path (/data/seed.txt)
        save_seed(hex_seed)

        return {"status": "ok"}

    except Exception:
        # Generic error response as per spec
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Decryption failed"},
        )


@app.get("/generate-2fa")
def generate_2fa():
    """
    GET /generate-2fa
    - Reads hex seed from /data/seed.txt
    - Generates current TOTP code
    - Calculates remaining validity seconds in this 30s period
    - Success: 200 { "code": "123456", "valid_for": 17 }
    - If seed missing: 500 { "error": "Seed not decrypted yet" }
    """
    if not os.path.exists("/data/seed.txt"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = load_seed()
        code = generate_totp_code(hex_seed)
        valid_for = seconds_remaining_in_period(30)

        return {"code": code, "valid_for": valid_for}

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to generate TOTP"},
        )


@app.post("/verify-2fa")
def verify_2fa(body: VerifyCodeRequest):
    """
    POST /verify-2fa
    - Accepts: { "code": "123456" }
    - Verifies against seed (±1 time period)
    - Missing code: 400 { "error": "Missing code" }
    - Seed missing: 500 { "error": "Seed not decrypted yet" }
    - Success: 200 { "valid": true/false }
    """
    # Validate input
    if body.code is None or body.code == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Missing code"},
        )

    # Check seed availability
    if not os.path.exists("/data/seed.txt"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = load_seed()
        is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)

        return {"valid": is_valid}

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Verification error"},
        )
