import requests

# Configure these based on your setup
BASE_URL = "http://localhost:8000"  # Adjust if different
LOGIN_ENDPOINT = "/api/v1/login"  # Try this first; if 405, try "/api/v1/auth/login" or check app/api/v1/login.py for the exact path

url = f"{BASE_URL}{LOGIN_ENDPOINT}"
payload = {
    "username": "potymatic@gmail.com",  # Change key to "email" if endpoint expects it
    "password": "Abcd1234@"
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"  # Try "application/json" if this fails
}

try:
    response = requests.post(url, data=payload, headers=headers)  # Change to json=payload if using JSON
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        response_json = response.json()
        token = response_json.get("access_token")  # Adjust if key is "token"
        token_type = response_json.get("token_type", "bearer")
        print(f"Access Token: {token}")
        print(f"Token Type: {token_type}")
        print("\nCopy 'Access Token' and paste as TOKEN in debug_proforma_invoices_endpoint.py, then rerun it.")
    else:
        print("Error Details:")
        print(response.json())
except requests.RequestException as e:
    print(f"Request failed: {e}")