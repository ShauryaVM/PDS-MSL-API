# mars_image_api.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import random

app = FastAPI(title="Mars Image API")

# Enable CORS if needed for frontend use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base URL of Netlify-hosted image directory
NETLIFY_BASE_URL = "https://pds-msl-imagequery.netlify.app"

@app.get("/api/images")
def get_image_urls(
    split: str = Query("train", enum=["train", "validation", "test"]),
    max_rows: int = Query(10, gt=0, le=1000)
):
    try:
        index_url = f"{NETLIFY_BASE_URL}/{split}/index.html"
        response = requests.get(index_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        image_links = [a['href'] for a in soup.find_all("a") if a['href'].lower().endswith(('.jpg', '.jpeg', '.png'))]
        full_urls = [f"{NETLIFY_BASE_URL}/{split}/{fname}" for fname in image_links]
        random.shuffle(full_urls)

        return {"images": full_urls[:max_rows]}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to fetch or parse index: {str(e)}"})
