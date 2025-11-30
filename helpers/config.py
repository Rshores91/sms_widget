import os

MARKETING_API_URL = os.getenv("MARKETING_API_URL", "http://localhost:8080")
SERVICE_USERNAME = os.getenv("SERVICE_USERNAME")
SERVICE_PASSWORD = os.getenv("SERVICE_PASSWORD")
TOKEN_TTL = int(os.getenv("TOKEN_TTL_SECONDS", "3000"))

