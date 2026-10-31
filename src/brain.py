import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from knowledge import KNOWLEDGE
from llm import ask_llm, get_last_status
from predict import check_url

intent_model = joblib.load("models/chitti_intent_model.pkl")

kb_vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
kb_matrix = kb_vec.fit_transform([f"{q} {q} {a}" for q, a in KNOWLEDGE])

URL_REGEX = re.compile(r"(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:[/?#]\S*)?", re.I)

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "iloveyou",
    "admin", "welcome", "letmein", "111111", "password1", "india123",
}
SCAM_WORDS = [
    "otp", "urgent", "kyc", "blocked", "suspended", "lottery", "prize",
    "winner", "gift", "verify", "click here", "claim", "refund", "expire",
    "expires", "bank", "pan", "aadhaar", "reward", "free", "immediately",
]

INTRO = (
    "Hi, I am Chitti, the robot. Speed: 1 terahertz. Memory: 1 zettabyte.\n"
    "(That is my movie-style intro. In real life I run on a cloud server.)\n\n"
    "I was built by Kishan Tiwari. Here is what I can do:\n"
    "- answer questions on studies, history, politics and general knowledge\n"
    "- write code for you\n"
    "- check if a link is phishing\n"
    "- check password strength\n"
    "- check a suspicious SMS or message for scam signs\n"
    "I cannot generate images."
)


def out(intent, reply, status=None, notes=""):
    return {"intent": intent, "reply": reply, "status": status, "notes": notes}


def predict_intent(text):
    probs = intent_model.predict_proba([text.lower()])[0]
    i = int(probs.argmax())
    return str(intent_model.classes_[i]), float(probs[i])


def answer_question(text, threshold=0.12):
    sims = cosine_similarity(kb_vec.transform([text]), kb_matrix)[0]
    best = int(sims.argmax())
    if sims[best] < threshold:
        return None
    return KNOWLEDGE[best][1]


def handle_urls(urls):
    lines, notes, bad = [], [], False
    for u in urls[:3]:
        r = check_url(u)
        pct = round(r["phishing_probability"] * 100)
        if r["verdict"] == "PHISHING":
            bad = True
            lines.append(f"Dangerous: {u} looks like PHISHING ({pct}% risk). "
                         "Do not open it or enter any details.")
        else:
            lines.append(f"Looks safe: {u} (risk score {pct}%). "
                         "Still be careful with links you did not expect.")
        if r["reasons"]:
            notes.append(f"{u}: " + "; ".join(r["reasons"]))
    return lines, notes, bad


def extract_password(text):
    m = re.search(r"['\"](.+?)['\"]", text)
    if m:
        return m.group(1)
    m = re.search(r"password\s*(?:is|:|=)\s*(\S+)", text, re.I)
    return m.group(1) if m else None


def check_password(pw):
    tips = []
    n = len(pw)
    length_pts = 2 if n >= 12 else 1 if n >= 8 else 0
    if n < 12:
        tips.append("use at least 12 characters")

    classes = [
        any(c.islower() for c in pw),
        any(c.isupper() for c in pw),
        any(c.isdigit() for c in pw),
        any(not c.isalnum() for c in pw),
    ]
    if not all(classes):
        tips.append("mix lowercase, uppercase, numbers and symbols")

    score = length_pts + sum(classes)
    if re.search(r"(.)\1\1", pw):
        score -= 1
        tips.append("avoid repeated characters like aaa")
    if re.search(r"(123|234|345|abc|qwe)", pw.lower()):
        score -= 1
        tips.append("avoid simple sequences like 123 or abc")
    if pw.lower() in COMMON_PASSWORDS:
        score = 0
        tips.append("this is a very common password")

    rating = "weak" if score <= 2 else "medium" if score <= 4 else "strong"
    return {"rating": rating, "score": max(score, 0), "tips": tips}


def handle_password(text):
    pw = extract_password(text)
    if not pw:
        return out("check_password",
                   "Send it like this: check password: Summer@2024. "
                   "Please use a sample password, never your real one.")
    r = check_password(pw)
    status = {"weak": "bad", "medium": None, "strong": "safe"}[r["rating"]]
    notes = "How to improve: " + "; ".join(r["tips"]) if r["tips"] else ""
    return out("check_password",
               f"Password strength: {r['rating'].upper()}.\n"
               "Tip: never type your real passwords into any chat or website.",
               status, notes)


def handle_scam(text, urls):
    low = text.lower()
    hits = [w for w in SCAM_WORDS if re.search(r"\b" + re.escape(w) + r"\b", low)]
    if not urls and not hits and len(text.split()) < 8:
        return out("scam_message",
                   "Paste the full message here and I will check it for scam signs.")

    lines, notes, bad = [], [], False
    if urls:
        lines, notes, bad = handle_urls(urls)
    if len(hits) >= 3:
        bad = True

    if bad:
        head = ("This message has strong scam warning signs. "
                "Do not click links, call back unknown numbers or share any OTP.")
    elif hits:
        head = "I found a few warning words, so be careful and verify with the official source."
    else:
        head = "I did not find clear scam signs, but never share your OTP or PIN with anyone."

    if hits:
        notes.append("Warning words: " + ", ".join(hits))
    return out("scam_message", "\n".join([head] + lines),
               "bad" if bad else None, " | ".join(notes))


def respond(message, history=None, allow_llm=True):
    text = message.strip()
    urls = URL_REGEX.findall(text)
    intent, conf = predict_intent(text)
    explicit = bool(re.search(r"https?://|www\.", text, re.I))

    if (urls and intent not in ("scam_message", "check_password")
            and "```" not in text
            and (explicit or intent == "check_url" or len(text.split()) <= 4)):
        intent = "check_url"
    elif conf < 0.25:
        intent = "unknown"

    if intent == "greeting":
        return out(intent, "Hi! I am Chitti. Ask me anything: studies, code, general "
                           "knowledge, or send a link, password or message to check.")
    if intent == "about":
        return out(intent, INTRO)
    if intent == "creator":
        return out(intent, "I was created by Kishan Tiwari, a BSc IT student. "
                           "He built my security brain, and I keep learning new skills.")
    if intent == "image_request":
        return out(intent, "I cannot generate or draw images. But I can help with "
                           "studies, code, security checks and general questions.")
    if intent == "thanks":
        return out(intent, "You are welcome! Stay safe online.")
    if intent == "check_url":
        if not urls:
            return out(intent, "Paste the link and I will check it.")
        lines, notes, bad = handle_urls(urls)
        return out(intent, "\n".join(lines), "bad" if bad else "safe", " | ".join(notes))
    if intent == "check_password":
        return handle_password(text)
    if intent == "scam_message":
        return handle_scam(text, urls)

    strong = answer_question(text, 0.35)
    if intent == "security_qa" and strong:
        return out("security_qa", strong)

    reply = ask_llm(text, history) if allow_llm else None
    if reply:
        return out("llm", reply)

    weak = answer_question(text, 0.12)
    if weak:
        return out("security_qa", weak)

    if not allow_llm:
        return out("unknown",
                   "You have reached today's limit of AI answers on this demo. "
                   "Please come back tomorrow. I can still check links, passwords "
                   "and suspicious messages.")
    if get_last_status() == "rate_limit":
        return out("unknown",
                   "I have used up my free AI quota for now, so I cannot answer open "
                   "questions. Please try again in a few minutes, or later if the daily "
                   "quota is finished. I can still check links, passwords and "
                   "suspicious messages.")
    return out("unknown",
               "My AI language model is not connected right now, so I cannot answer "
               "open questions. I can still check links, passwords and suspicious messages.")