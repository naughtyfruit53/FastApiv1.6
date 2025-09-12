import requests
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYxNDc0NjAsInN1YiI6InBvdHltYXRpY0BnbWFpbC5jb20iLCJvcmdhbml6YXRpb25faWQiOjEsInVzZXJfcm9sZSI6Im9yZ19hZG1pbiIsInVzZXJfdHlwZSI6Im9yZ2FuaXphdGlvbiJ9.Y9iDNYHpMVPpXb-NFrxPhSZRefeKwwWQuNZjoeMERHY'}
response = requests.get('http://localhost:8000/api/v1/organizations/current', headers=headers)
print(response.json())