import requests

# Base URL of your FastAPI backend (adjust if running on different port/host)
url = "http://127.0.0.1:8000/api/v1/stock"  # Assuming default Uvicorn port; change if needed

# Your JWT token - using multiline string to handle length and avoid syntax errors
token = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTU1MDQ5MjksInN1YiI6InBvdHltYXRpY0BnbWFpbC5jb20iLCJvcmdhbml6YXRpb25faWQiOjEsInVzZXJfcm9sZSI6Im9yZ19hZG1pbiIsInVzZXJfdHlwZSI6Im9yZ2FuaXphdGlvbiJ9.Zhmd2lYNBd64aEj3CfsSNrJaFmKxAHOKDjzS1LLDyRE"
)

# Headers with authorization
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

# Simulate the frontend params (adjust based on what frontend might be sending; start with empty to replicate logs)
params = {
    # 'search': '',  # Uncomment and set if frontend sends this
    # 'show_zero': False,  # Uncomment if sent
    # Add other suspected params like 'product_id': None or '' to test
}

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 422:
        print("422 Error Details:")
        print(response.json())  # This will show the validation error message, e.g., invalid product_id type
    else:
        print("Response Data:")
        print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")