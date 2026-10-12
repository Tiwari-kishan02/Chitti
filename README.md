# Chitti: AI Security Assistant

![CI](https://github.com/Tiwari-kishan02/Chitti/actions/workflows/ci.yml/badge.svg)

Chitti detects phishing URLs using a machine learning model (XGBoost) and serves predictions through a FastAPI REST API. The project is containerized with Docker and tested automatically with GitHub Actions.

## Features
- Phishing URL detection from 26 engineered URL features
- REST API with automatic docs at `/docs`
- Automated tests (pytest) and CI pipeline
- Docker support

## Model results
- Accuracy: about 95% on a held-out test set
- Phishing precision: about 91%, recall: about 80%
- Training data: Kaggle "Phishing Site URLs" dataset plus the top 50,000 domains from the Tranco list as extra safe examples

## Project structure
```
src/     feature extraction, training, prediction
app/     FastAPI application
tests/   pytest tests
models/  trained model
```

## Run locally
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs and try the `/predict` endpoint.

## Example
Request:
```
{"url": "secure-paypal-login.verify-account.xyz/webscr.php?cmd=login"}
```
Response:
```
{"url": "...", "verdict": "PHISHING", "phishing_probability": 0.999}
```

## Run with Docker
```
docker build -t chitti .
docker run -p 8000:8000 chitti
```

## Limitations
The model uses only URL text features, so it can miss phishing links that look normal. Future work: page content analysis, WHOIS data, and a chat interface.