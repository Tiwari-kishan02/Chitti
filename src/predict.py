import sys
import joblib
import pandas as pd
from features import extract_features

bundle = joblib.load("models/chitti_url_model.pkl")
model, cols = bundle["model"], bundle["features"]


def check_url(url):
    row = pd.DataFrame([extract_features(url)])[cols]
    prob = float(model.predict_proba(row)[0][1])
    return {
        "url": url,
        "verdict": "PHISHING" if prob >= 0.5 else "SAFE",
        "phishing_probability": round(prob, 3),
    }


if __name__ == "__main__":
    tests = sys.argv[1:] or [
        "https://www.google.com",
        "paypal.com.secure-login.verify-account.xyz/webscr.php?cmd=login",
    ]
    for t in tests:
        print(check_url(t))