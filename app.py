from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import requests

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VIDEO_API_KEY = os.getenv("VIDEO_API_KEY")

if not PEXELS_API_KEY:
    raise RuntimeError("PEXELS_API_KEY missing in .env")

# --------------------------------------------------
# Disable OpenAPI / Docs
# --------------------------------------------------
app = FastAPI(
    title="Media Backend API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# --------------------------------------------------
# Request Models
# --------------------------------------------------
class MediaRequest(BaseModel):
    type: str
    prompt: str
    orientation: str = "landscape"

# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.get("/")
def home():
    return {"status": "Backend running without RAG"}

# --------------------------------------------------
# IMAGE GENERATION (Pexels)
# --------------------------------------------------
@app.post("/generate-image")
def generate_image(payload: MediaRequest):

    if payload.type != "image":
        raise HTTPException(status_code=400, detail="Only image type supported")

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": payload.prompt,
        "per_page": 1,
        "orientation": payload.orientation
    }

    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch from Pexels")

    data = response.json()

    if not data.get("photos"):
        raise HTTPException(status_code=404, detail="No images found")

    photo = data["photos"][0]

    return {
        "media_type": "image",
        "image_url": photo["src"]["large"],
        "photographer": photo["photographer"],
        "source": "pexels"
    }

# --------------------------------------------------
# VIDEO GENERATION (Example Structure)
# Replace URL with your real video API
# --------------------------------------------------
@app.post("/generate-video")
def generate_video(payload: MediaRequest):

    if payload.type != "video":
        raise HTTPException(status_code=400, detail="Only video type supported")

    headers = {
        "Authorization": f"Bearer {VIDEO_API_KEY}"
    }

    body = {
        "prompt": payload.prompt
    }

    response = requests.post(
        "https://your-video-api.com/generate",
        headers=headers,
        json=body,
        timeout=20
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Video API failed")

    return response.json()
