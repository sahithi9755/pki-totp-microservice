from app.crypto_utils import (
    load_private_key,
    decrypt_seed,
    generate_totp_code,
    verify_totp_code,
)

# Use the same encrypted_seed.txt you got in Step 5
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

priv = load_private_key("student_private.pem")

hex_seed = decrypt_seed(encrypted_seed_b64, priv)
print("Decrypted seed:", hex_seed)

code = generate_totp_code(hex_seed)
print("Current TOTP code:", code)

print("Verify (should be True):", verify_totp_code(hex_seed, code, valid_window=1))
