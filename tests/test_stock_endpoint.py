# test_stock_endpoint.py - Run this script to test /api/v1/stock and see exact 422 error details

import requests

# Configuration - Update these
BASE_URL = "http://127.0.0.1:8000/api/v1/stock"  # Your API base URL
LOGIN_URL = "http://127.0.0.1:8000/api/v1/auth/login"  # Changed to match tokenUrl from security.py
EMAIL = "potymatic@gmail.com"  # Use email as key, since logs show email-based query
PASSWORD = "Abcd1234@"  # Replace with real password; not in .env

# First, login to get token
login_data = {
    "username": EMAIL,  # Tutorial uses "username", but it can be email; if fails, try "email": EMAIL
    "password": PASSWORD,
}
# Try form data first (as per OAuth2 tutorial)
login_response = requests.post(LOGIN_URL, data=login_data)

if login_response.status_code != 200:
    print(f"Login failed with form data: {login_response.status_code} - {login_response.text}")
    # Alternative: Try JSON body
    login_response = requests.post(LOGIN_URL, json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed with JSON: {login_response.status_code} - {login_response.text}")
        print("Hints:")
        print("1. Ensure Uvicorn is running: uvicorn app.main:app --reload --port 8000")
        print("2. Check Swagger: Open http://127.0.0.1:8000/docs in browser, find the login endpoint, note the exact path and method.")
        print("3. If endpoint is /token, change LOGIN_URL to 'http://127.0.0.1:8000/api/v1/auth/token'")
        print("4. If 'username' fails, try login_data = {'email': EMAIL, 'password': PASSWORD}")
        print("5. Verify route code: In app/api/v1/auth.py or login.py, look for @router.post('/login') and the body type (OAuth2PasswordRequestForm for form, or Pydantic model for JSON).")
        print("6. Credentials: Ensure user exists and password is correct; try resetting if needed")
        exit(1)

token = login_response.json().get("access_token")
if not token:
    print("No token in response:", login_response.json())
    exit(1)

print(f"Obtained token: {token[:20]}...")  # Partial print for security

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

# Test cases: various param combinations
test_cases = [
    {},  # No params
    {"skip": 0, "limit": 100, "search": "", "show_zero": False},  # Default-like
    {"product_id": ""},  # Empty product_id (should cause 422 if not handled)
    {"product_id": "abc"},  # Invalid int
    {"product_id": 1},  # Valid product_id (adjust to existing ID if known)
    {"show_zero": "invalid"},  # Invalid bool
    {"search": "test"},  # Valid search
]

for i, params in enumerate(test_cases, 1):
    print(f"\nTest Case {i}: Params = {params}")
    response = requests.get(BASE_URL, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 422:
        print("Error Details:", response.json())  # Prints the validation error message
    else:
        print("Response Data:", response.json())