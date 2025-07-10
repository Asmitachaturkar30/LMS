import requests

def send_kyc_request(base_url, endpoint, token, payload):
    try:
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code, response.json()
    except Exception as e:
        return 500, {"error": str(e)}
