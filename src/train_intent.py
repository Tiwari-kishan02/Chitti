import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline, make_union

from intents_data import INTENTS

texts, labels = [], []
for intent, phrases in INTENTS.items():
    for p in phrases:
        texts.append(p.lower())
        labels.append(intent)

print("Total examples:", len(texts), "| Intents:", len(INTENTS))

model = make_pipeline(
    make_union(
        TfidfVectorizer(ngram_range=(1, 2)),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)),
    ),
    LogisticRegression(max_iter=1000, C=10),
)

scores = cross_val_score(model, texts, labels, cv=5)
print("Cross-validation accuracy:", round(scores.mean(), 3))

model.fit(texts, labels)
joblib.dump(model, "models/chitti_intent_model.pkl")
print("Saved: models/chitti_intent_model.pkl")