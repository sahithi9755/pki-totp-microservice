import base64
import subprocess

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def load_private_key(path: str = "student_private.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(path: str = "instructor_public.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def sign_message(message: str, private_key) -> bytes:
    """
    Sign commit hash using RSA-PSS with SHA-256 and max salt length.
    """
    message_bytes = message.encode("utf-8")
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt signature using RSA/OAEP with SHA-256 and MGF1(SHA-256).
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


def get_latest_commit_hash() -> str:
    """
    Get latest commit hash (40-character hex) using git.
    """
    result = subprocess.check_output(
        ["git", "log", "-1", "--format=%H"],
        text=True,
    )
    return result.strip()


def main():
    # 1. Get commit hash
    commit_hash = get_latest_commit_hash()
    print("Commit Hash:", commit_hash)

    # 2. Load keys
    private_key = load_private_key("student_private.pem")
    instructor_pub = load_public_key("instructor_public.pem")

    # 3. Sign commit hash
    signature = sign_message(commit_hash, private_key)

    # 4. Encrypt signature with instructor public key
    encrypted_signature = encrypt_with_public_key(signature, instructor_pub)

    # 5. Base64 encode the encrypted signature (single line)
    encrypted_b64 = base64.b64encode(encrypted_signature).decode("ascii")

    print("Encrypted Commit Signature (Base64, single line):")
    print(encrypted_b64)


if __name__ == "__main__":
    main()
