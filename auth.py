import urllib.parse
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "b28825f8812c456fb3a7cac95e5bb5c4")
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:5050/callback")
SCOPE = "user-top-read user-library-read"

def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true"
    }
    return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code):
    token_url = "https://accounts.spotify.com/api/token"
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    base64_creds = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {base64_creds}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)
    return response.json(), response.status_code


def refresh_token(refresh_token_value):
    token_url = "https://accounts.spotify.com/api/token"
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    base64_creds = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {base64_creds}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value
    }

    response = requests.post(token_url, headers=headers, data=data)
    return response.json(), response.status_code