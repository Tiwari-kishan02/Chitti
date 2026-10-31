import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "src"))

from fastapi.testclient import TestClient
from app.main import app
from features import extract_features

client = TestClient(app)


def test_home():
    r = client.get("/")
    assert r.status_code == 200


def test_ip_features():
    f = extract_features("http://192.168.1.1/login.php")
    assert f["has_ip"] == 1
    assert f["has_php"] == 1


def test_safe_url():
    r = client.post("/predict", json={"url": "google.com"})
    assert r.status_code == 200
    assert r.json()["verdict"] == "SAFE"


def test_phishing_url():
    url = "secure-paypal-login.verify-account.xyz/webscr.php?cmd=login"
    r = client.post("/predict", json={"url": url})
    assert r.json()["verdict"] == "PHISHING"


def test_empty_url():
    r = client.post("/predict", json={"url": "   "})
    assert r.status_code == 400


def test_reasons_present():
    url = "secure-paypal-login.verify-account.xyz/webscr.php?cmd=login"
    r = client.post("/predict", json={"url": url})
    assert len(r.json()["reasons"]) > 0



def test_chat_creator():
    r = client.post("/chat", json={"message": "who made you"})
    assert r.json()["intent"] == "creator"
    assert "Kishan Tiwari" in r.json()["reply"]


def test_chat_no_images():
    r = client.post("/chat", json={"message": "generate an image of a cat"})
    assert r.json()["intent"] == "image_request"


def test_chat_intro():
    r = client.post("/chat", json={"message": "who are you"})
    assert "terahertz" in r.json()["reply"].lower()



def test_detect_lang():
    from brain import detect_lang
    assert detect_lang("who are you") == "en"
    assert detect_lang("tum kaun ho") == "hinglish"
    assert detect_lang("तुम कौन हो") == "hi"


def test_chat_creator_hinglish():
    r = client.post("/chat", json={"message": "tumhe kisne banaya hai"})
    assert r.json()["intent"] == "creator"
    assert "Kishan Tiwari" in r.json()["reply"]


def test_chat_about_hindi():
    r = client.post("/chat", json={"message": "तुम कौन हो"})
    assert r.json()["intent"] == "about"
    assert "चिट्टी" in r.json()["reply"]