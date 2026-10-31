import datetime
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from predict import check_url
from brain import respond

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Chitti",
    description="AI assistant: security skills plus general knowledge and code help",
    version="0.5.0",
)

HITS = defaultdict(deque)
LIMIT, WINDOW = 20, 60  # max 20 chat requests per minute per IP

AI_USED = defaultdict(int)
DAILY_AI_LIMIT = 30  # max AI (LLM) answers per visitor per day


def too_many_requests(ip):
    now = time.time()
    q = HITS[ip]
    while q and now - q[0] > WINDOW:
        q.popleft()
    if len(q) >= LIMIT:
        return True
    q.append(now)
    return False


class URLRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"message": "Chitti is running"}


@app.post("/predict")
def predict(req: URLRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    return check_url(req.url)


@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(req.message) > 4000:
        raise HTTPException(status_code=400, detail="Message is too long (max 4000 characters).")

    ip = (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
          or (request.client.host if request.client else "unknown"))
    if too_many_requests(ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute and try again.")

    day = datetime.date.today().isoformat()
    for k in list(AI_USED):
        if k[1] != day:
            del AI_USED[k]
    key = (ip, day)

    result = respond(req.message, req.history, allow_llm=AI_USED[key] < DAILY_AI_LIMIT)
    if result.get("intent") == "llm":
        AI_USED[key] += 1
    return result