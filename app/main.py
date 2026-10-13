import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from predict import check_url

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Chitti",
    description="AI security assistant: phishing URL detection",
    version="0.2.0",
)


class URLRequest(BaseModel):
    url: str


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"message": "Chitti is running"}


@app.post("/predict")
def predict(req: URLRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL empty hai")
    return check_url(req.url)