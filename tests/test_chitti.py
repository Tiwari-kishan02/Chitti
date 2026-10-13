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