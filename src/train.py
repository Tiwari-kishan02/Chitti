import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
from features import extract_features

print("Loading data...")
df = pd.read_csv("data/phishing_site_urls.csv")
df = df.dropna()
df["target"] = (df["Label"].str.lower() == "bad").astype(int)

# Popular websites ko extra "good" examples ki tarah jodo
top = pd.read_csv("data/tranco.csv", header=None,
                  names=["rank", "domain"], nrows=50000)
extra_urls = []
for d in top["domain"].astype(str):
    extra_urls.append(d)
    extra_urls.append("www." + d)
extra = pd.DataFrame({"URL": extra_urls, "Label": "good", "target": 0})

df = pd.concat([df, extra], ignore_index=True)
df = df.drop_duplicates(subset="URL")
print(df["Label"].value_counts())

print("Extracting features (2-4 minute lagenge)...")
X = pd.DataFrame([extract_features(u) for u in df["URL"]])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training model...")
model = XGBClassifier(
    n_estimators=300, max_depth=8, learning_rate=0.1,
    n_jobs=-1, eval_metric="logloss"
)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print("\nAccuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, target_names=["good", "bad"]))
print("Confusion matrix:\n", confusion_matrix(y_test, pred))

joblib.dump({"model": model, "features": list(X.columns)},
            "models/chitti_url_model.pkl")
print("\nModel saved: models/chitti_url_model.pkl")