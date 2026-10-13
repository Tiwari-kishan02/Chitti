import sys
import joblib
import pandas as pd
from features import extract_features

bundle = joblib.load("models/chitti_url_model.pkl")
model, cols = bundle["model"], bundle["features"]


def explain(f):
    reasons = []
    if f["has_ip"]:
        reasons.append("website address is a raw IP address")
    if f["at_symbol"]:
        reasons.append("URL contains an @ symbol")
    if f["host_keyword_count"]:
        reasons.append("domain has words like login, secure or paypal")
    if f["host_hyphens"] >= 2:
        reasons.append("domain has many hyphens")
    if f["subdomains"] >= 3:
        reasons.append("too many subdomains")
    if f["url_length"] > 75:
        reasons.append("URL is very long")
    if f["has_php"]:
        reasons.append("points to a .php page")
    if f["has_exe"]:
        reasons.append("points to an .exe file")
    return reasons


def check_url(url):
    f = extract_features(url)
    row = pd.DataFrame([f])[cols]
    prob = float(model.predict_proba(row)[0][1])
    return {
        "url": url,
        "verdict": "PHISHING" if prob >= 0.5 else "SAFE",
        "phishing_probability": round(prob, 3),
        "reasons": explain(f),
    }


if __name__ == "__main__":
    tests = sys.argv[1:] or [
        "https://www.google.com",
        "paypal.com.secure-login.verify-account.xyz/webscr.php?cmd=login",
    ]
    for t in tests:
        print(check_url(t))