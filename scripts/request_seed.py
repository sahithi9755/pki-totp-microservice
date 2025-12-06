import json
import requests

INSTRUCTOR_API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed(student_id: str, github_repo_url: str, api_url: str = INSTRUCTOR_API_URL):
    # 1. Read student public key
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()

    # Convert newlines to \n (important requirement)
    public_key_single_line = public_key_pem.replace("\n", "\\n")

    # 2. Prepare JSON payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem
    }

    # 3. Send POST request
    response = requests.post(api_url, json=payload, timeout=10)

    data = response.json()

    if data.get("status") != "success":
        raise Exception("Failed to fetch encrypted seed: " + str(data))

    encrypted_seed = data["encrypted_seed"]

    # 4. Save encrypted_seed.txt
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Encrypted seed saved to encrypted_seed.txt")

if __name__ == "__main__":
    STUDENT_ID = "23A91A0515"
    GITHUB_REPO_URL = "https://github.com/sahithi9755/pki-totp-microservice"

    request_seed(STUDENT_ID, GITHUB_REPO_URL)
