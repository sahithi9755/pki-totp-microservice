from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_keypair(key_size: int = 4096):
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # Generate public key
    public_key = private_key.public_key()

    # Convert private key → PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Convert public key → PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Save files
    with open("student_private.pem", "wb") as f:
        f.write(private_pem)

    with open("student_public.pem", "wb") as f:
        f.write(public_pem)

    print("Keys generated: student_private.pem, student_public.pem")


if __name__ == "__main__":
    generate_rsa_keypair()
