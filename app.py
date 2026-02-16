import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GPT + OAuth + YouTube Backend")

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI")

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# ⚠ In production use database
token_store = {}

def build_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )

@app.get("/auth/start")
def auth_start():
    flow = build_flow()
    flow.redirect_uri = REDIRECT_URI

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    return RedirectResponse(auth_url)


@app.get("/auth/callback")
def auth_callback(request: Request):
    flow = build_flow()
    flow.redirect_uri = REDIRECT_URI

    flow.fetch_token(authorization_response=str(request.url))

    credentials = flow.credentials

    token_store["admin"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    return {"message": "OAuth successful"}


@app.get("/yt/my-channel")
def my_channel():
    if "admin" not in token_store:
        raise HTTPException(status_code=401, detail="Not authenticated")

    creds_data = token_store["admin"]

    credentials = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=SCOPES
    )

    headers = {
        "Authorization": f"Bearer {credentials.token}"
    }

    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        headers=headers,
        params={
            "part": "snippet,statistics",
            "mine": "true"
        }
    )

    return r.json()


