import requests

# Configure these
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/proforma-invoices"
TOKEN = "your_jwt_token_here"  # Paste token here after getting it from login script

url = f"{BASE_URL}{ENDPOINT}"
params = {
    "skip": 0,
    "limit": 100
}
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

try:
    response = requests.get(url, params=params, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON (Vouchers List):")
        print(response.json())
    else:
        print("Error Details:")
        print(response.json())
except requests.RequestException as e:
    print(f"Request failed: {e}")