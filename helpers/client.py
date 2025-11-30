import requests
from .config import MARKETING_API_URL
from .token import get_service_token

def create_customer(payload):
    resp = requests.post(f"{MARKETING_API_URL}/api/customer", json=payload, timeout=10)
    resp.raise_for_status()
    return resp

def send_sms(phone, body, customer_id=None):
    token = get_service_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"PhoneNumber": phone, "Body": body, "CustomerId": customer_id}
    resp = requests.post(f"{MARKETING_API_URL}/api/notifications/sms", json=payload, headers=headers, timeout=10)
    return resp