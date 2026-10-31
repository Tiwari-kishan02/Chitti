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

# ---------------- language detection ----------------
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
HINGLISH_WORDS = {
    "kya", "hai", "hain", "ho", "kaun", "kon", "tum", "tumhe", "tumko", "tumhara",
    "aap", "aapko", "aapka", "mujhe", "mera", "meri", "mere", "main", "batao", "bata",
    "bataiye", "kaise", "kese", "nahi", "nhi", "karo", "kar", "kro", "karna", "kare",
    "dena", "dijiye", "chahiye", "chahta", "chahti", "ka", "ki", "ke", "ko", "se",
    "mein", "mai", "pe", "aur", "ye", "yeh", "wo", "woh", "kisne", "kisko", "kyun",
    "kyu", "kaha", "kahan", "kab", "kitna", "kitne", "banaya", "banao", "likh", "likho",
    "samjhao", "sikhao", "hoga", "hogi", "tha", "thi", "abhi", "bhi", "toh", "accha",
    "acha", "theek", "dost", "bhai", "namaste", "shukriya", "dhanyavad", "kuch", "koi",
    "mat", "bolo", "dikhao", "sawal", "jawab", "hota", "hoti", "hoon", "sakta", "sakte",
}


def detect_lang(text):
    if DEVANAGARI.search(text):
        return "hi"
    words = re.findall(r"[a-z]+", text.lower())
    hits = sum(1 for w in words if w in HINGLISH_WORDS)
    if hits >= 2 or (hits >= 1 and len(words) <= 3):
        return "hinglish"
    return "en"


# ---------------- fixed replies in 3 languages ----------------
STRINGS = {
    "greeting": {
        "en": "Hi! I am Chitti. Ask me anything: studies, code, general knowledge, or send a link, password or message to check.",
        "hinglish": "Hi! Main Chitti hoon. Mujhse kuch bhi poocho: padhai, code, general knowledge, ya koi link, password ya message check karwao.",
        "hi": "नमस्ते! मैं चिट्टी हूँ। मुझसे कुछ भी पूछिए: पढ़ाई, कोड, सामान्य ज्ञान, या कोई लिंक, पासवर्ड या मैसेज जाँचने को दीजिए।",
    },
    "about": {
        "en": (
            "Hi, I am Chitti, the robot. Speed: 1 terahertz. Memory: 1 zettabyte.\n"
            "(That is my movie-style intro. In real life I run on a cloud server.)\n\n"
            "I was built by Kishan Tiwari. Here is what I can do:\n"
            "- answer questions on studies, history, politics and general knowledge\n"
            "- write code for you\n"
            "- check if a link is phishing\n"
            "- check password strength\n"
            "- check a suspicious SMS or message for scam signs\n"
            "I cannot generate images."
        ),
        "hinglish": (
            "Hi, main Chitti hoon, the robot. Speed: 1 terahertz. Memory: 1 zettabyte.\n"
            "(Ye meri movie-style intro hai. Asli mein main ek cloud server pe chalta hoon.)\n\n"
            "Mujhe Kishan Tiwari ne banaya hai. Main ye sab kar sakta hoon:\n"
            "- padhai, history, politics aur general knowledge ke sawaalon ke jawab\n"
            "- aapke liye code likhna\n"
            "- check karna ki link phishing hai ya nahi\n"
            "- password ki strength check karna\n"
            "- kisi suspicious SMS ya message mein scam ke signs dhoondhna\n"
            "Main images generate nahi kar sakta."
        ),
        "hi": (
            "नमस्ते, मैं चिट्टी हूँ, रोबोट। स्पीड: 1 टेराहर्ट्ज़। मेमोरी: 1 ज़ेटाबाइट।\n"
            "(ये मेरा मूवी-स्टाइल इंट्रो है। असल में मैं एक क्लाउड सर्वर पर चलता हूँ।)\n\n"
            "मुझे किशन तिवारी ने बनाया है। मैं ये सब कर सकता हूँ:\n"
            "- पढ़ाई, इतिहास, राजनीति और सामान्य ज्ञान के सवालों के जवाब\n"
            "- आपके लिए कोड लिखना\n"
            "- जाँचना कि कोई लिंक फ़िशिंग है या नहीं\n"
            "- पासवर्ड की मज़बूती जाँचना\n"
            "- किसी संदिग्ध SMS या मैसेज में स्कैम के संकेत ढूँढना\n"
            "मैं इमेज नहीं बना सकता।"
        ),
    },
    "creator": {
        "en": "I was created by Kishan Tiwari, a BSc IT student. He built my security brain, and I keep learning new skills.",
        "hinglish": "Mujhe Kishan Tiwari ne banaya hai, jo BSc IT ke student hain. Unhone mera security brain banaya hai, aur main naye skills seekhta rehta hoon.",
        "hi": "मुझे किशन तिवारी ने बनाया है, जो BSc IT के छात्र हैं। उन्होंने मेरा सिक्योरिटी ब्रेन बनाया है, और मैं नई चीज़ें सीखता रहता हूँ।",
    },
    "image": {
        "en": "I cannot generate or draw images. But I can help with studies, code, security checks and general questions.",
        "hinglish": "Main images generate ya draw nahi kar sakta. Lekin padhai, code, security check aur general sawaalon mein madad kar sakta hoon.",
        "hi": "मैं इमेज नहीं बना या ड्रॉ कर सकता। लेकिन पढ़ाई, कोड, सिक्योरिटी चेक और सामान्य सवालों में मदद कर सकता हूँ।",
    },
    "thanks": {
        "en": "You are welcome! Stay safe online.",
        "hinglish": "Koi baat nahi! Online safe rehna.",
        "hi": "कोई बात नहीं! ऑनलाइन सुरक्षित रहिए।",
    },
    "paste_link": {
        "en": "Paste the link and I will check it.",
        "hinglish": "Link paste karo, main check kar dunga.",
        "hi": "लिंक पेस्ट कीजिए, मैं जाँच कर दूँगा।",
    },
    "url_bad": {
        "en": "Dangerous: {u} looks like PHISHING ({pct}% risk). Do not open it or enter any details.",
        "hinglish": "Khatarnak: {u} PHISHING lag raha hai ({pct}% risk). Ise na kholo aur koi details mat daalo.",
        "hi": "खतरनाक: {u} फ़िशिंग लग रहा है ({pct}% जोखिम)। इसे न खोलें और कोई जानकारी न दें।",
    },
    "url_safe": {
        "en": "Looks safe: {u} (risk score {pct}%). Still be careful with links you did not expect.",
        "hinglish": "Safe lag raha hai: {u} (risk score {pct}%). Phir bhi jo links aapne expect nahi kiye, unse savdhan rahein.",
        "hi": "सुरक्षित लग रहा है: {u} (जोखिम स्कोर {pct}%)। फिर भी जिन लिंक की आपको उम्मीद नहीं थी, उनसे सावधान रहें।",
    },
    "pw_usage": {
        "en": "Send it like this: check password: Summer@2024. Please use a sample password, never your real one.",
        "hinglish": "Aise bhejo: check password: Summer@2024. Sample password use karo, apna asli password kabhi mat bhejo.",
        "hi": "ऐसे भेजिए: check password: Summer@2024. कृपया सैंपल पासवर्ड इस्तेमाल करें, अपना असली पासवर्ड कभी न भेजें।",
    },
    "pw_result": {
        "en": "Password strength: {rating}.\nTip: never type your real passwords into any chat or website.",
        "hinglish": "Password strength: {rating}.\nTip: apne asli password kisi chat ya website mein kabhi type mat karo.",
        "hi": "पासवर्ड की मज़बूती: {rating}।\nसुझाव: अपने असली पासवर्ड कभी किसी चैट या वेबसाइट में न लिखें।",
    },
    "pw_improve": {
        "en": "How to improve: ",
        "hinglish": "Kaise sudhare: ",
        "hi": "कैसे सुधारें: ",
    },
    "scam_paste": {
        "en": "Paste the full message here and I will check it for scam signs.",
        "hinglish": "Poora message yahan paste karo, main scam signs check kar dunga.",
        "hi": "पूरा मैसेज यहाँ पेस्ट कीजिए, मैं स्कैम के संकेत जाँच लूँगा।",
    },
    "scam_bad": {
        "en": "This message has strong scam warning signs. Do not click links, call back unknown numbers or share any OTP.",
        "hinglish": "Is message mein scam ke strong signs hain. Links par click mat karo, anjaan numbers par call back mat karo aur koi OTP share mat karo.",
        "hi": "इस मैसेज में स्कैम के मज़बूत संकेत हैं। लिंक पर क्लिक न करें, अनजान नंबर पर कॉल बैक न करें और कोई OTP साझा न करें।",
    },
    "scam_some": {
        "en": "I found a few warning words, so be careful and verify with the official source.",
        "hinglish": "Mujhe kuch warning words mile hain, isliye savdhan rahein aur official source se verify karo.",
        "hi": "मुझे कुछ चेतावनी वाले शब्द मिले हैं, इसलिए सावधान रहें और आधिकारिक स्रोत से पुष्टि करें।",
    },
    "scam_none": {
        "en": "I did not find clear scam signs, but never share your OTP or PIN with anyone.",
        "hinglish": "Mujhe saaf scam signs nahi mile, lekin apna OTP ya PIN kisi ke saath share mat karo.",
        "hi": "मुझे स्पष्ट स्कैम संकेत नहीं मिले, लेकिन अपना OTP या PIN किसी से साझा न करें।",
    },
    "scam_words": {
        "en": "Warning words: ",
        "hinglish": "Warning words: ",
        "hi": "चेतावनी वाले शब्द: ",
    },
    "quota_cap": {
        "en": "You have reached today's limit of AI answers on this demo. Please come back tomorrow. I can still check links, passwords and suspicious messages.",
        "hinglish": "Aaj ke liye is demo mein AI jawabon ki limit poori ho gayi hai. Kal wapas aana. Main abhi bhi links, passwords aur suspicious messages check kar sakta hoon.",
        "hi": "आज के लिए इस डेमो में AI जवाबों की सीमा पूरी हो गई है। कल फिर आइए। मैं अभी भी लिंक, पासवर्ड और संदिग्ध मैसेज जाँच सकता हूँ।",
    },
    "quota_rate": {
        "en": "I have used up my free AI quota for now, so I cannot answer open questions. Please try again in a few minutes, or later if the daily quota is finished. I can still check links, passwords and suspicious messages.",
        "hinglish": "Meri free AI quota abhi ke liye khatam ho gayi hai, isliye open sawaalon ke jawab nahi de sakta. Kuch minute baad dobara try karo, ya baad mein agar daily quota khatam hai. Main links, passwords aur suspicious messages abhi bhi check kar sakta hoon.",
        "hi": "मेरा मुफ़्त AI कोटा अभी के लिए खत्म हो गया है, इसलिए खुले सवालों के जवाब नहीं दे सकता। कुछ मिनट बाद फिर कोशिश कीजिए, या बाद में अगर रोज़ का कोटा खत्म है। मैं लिंक, पासवर्ड और संदिग्ध मैसेज अभी भी जाँच सकता हूँ।",
    },
    "no_llm": {
        "en": "My AI language model is not connected right now, so I cannot answer open questions. I can still check links, passwords and suspicious messages.",
        "hinglish": "Mera AI language model abhi connected nahi hai, isliye open sawaalon ke jawab nahi de sakta. Main links, passwords aur suspicious messages abhi bhi check kar sakta hoon.",
        "hi": "मेरा AI लैंग्वेज मॉडल अभी जुड़ा नहीं है, इसलिए खुले सवालों के जवाब नहीं दे सकता। मैं लिंक, पासवर्ड और संदिग्ध मैसेज अभी भी जाँच सकता हूँ।",
    },
}

PW_RATING = {
    "en": {"weak": "WEAK", "medium": "MEDIUM", "strong": "STRONG"},
    "hinglish": {"weak": "KAMZOR", "medium": "MEDIUM", "strong": "MAZBOOT"},
    "hi": {"weak": "कमज़ोर", "medium": "मध्यम", "strong": "मज़बूत"},
}

# Hinglish / Hindi versions of the English reasons and tips
TRANSLATIONS = {
    "hinglish": {
        "website address is a raw IP address": "website ka address seedha IP address hai",
        "URL contains an @ symbol": "URL mein @ symbol hai",
        "domain has words like login, secure or paypal": "domain mein login, secure ya paypal jaise words hain",
        "domain has many hyphens": "domain mein bahut saare hyphens hain",
        "too many subdomains": "bahut zyada subdomains hain",
        "URL is very long": "URL bahut lamba hai",
        "points to a .php page": ".php page ki taraf le jata hai",
        "points to an .exe file": ".exe file ki taraf le jata hai",
        "use at least 12 characters": "kam se kam 12 characters rakho",
        "mix lowercase, uppercase, numbers and symbols": "small letters, capital letters, numbers aur symbols mix karo",
        "avoid repeated characters like aaa": "aaa jaise repeated characters se bacho",
        "avoid simple sequences like 123 or abc": "123 ya abc jaise simple sequences se bacho",
        "this is a very common password": "ye bahut common password hai",
    },
    "hi": {
        "website address is a raw IP address": "वेबसाइट का पता सीधा IP एड्रेस है",
        "URL contains an @ symbol": "URL में @ चिह्न है",
        "domain has words like login, secure or paypal": "डोमेन में login, secure या paypal जैसे शब्द हैं",
        "domain has many hyphens": "डोमेन में बहुत सारे हाइफ़न हैं",
        "too many subdomains": "बहुत ज़्यादा सबडोमेन हैं",
        "URL is very long": "URL बहुत लंबा है",
        "points to a .php page": ".php पेज की ओर ले जाता है",
        "points to an .exe file": ".exe फ़ाइल की ओर ले जाता है",
        "use at least 12 characters": "कम से कम 12 अक्षर रखें",
        "mix lowercase, uppercase, numbers and symbols": "छोटे-बड़े अक्षर, अंक और चिह्न मिलाएँ",
        "avoid repeated characters like aaa": "aaa जैसे दोहराए गए अक्षरों से बचें",
        "avoid simple sequences like 123 or abc": "123 या abc जैसे आसान क्रम से बचें",
        "this is a very common password": "ये बहुत आम पासवर्ड है",
    },
}


def t(key, lang, **kw):
    s = STRINGS[key][lang]
    return s.format(**kw) if kw else s


def tr(items, lang):
    if lang == "en":
        return items
    table = TRANSLATIONS[lang]
    return [table.get(i, i) for i in items]


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


def handle_urls(urls, lang):
    lines, notes, bad = [], [], False
    for u in urls[:3]:
        r = check_url(u)
        pct = round(r["phishing_probability"] * 100)
        if r["verdict"] == "PHISHING":
            bad = True
            lines.append(t("url_bad", lang, u=u, pct=pct))
        else:
            lines.append(t("url_safe", lang, u=u, pct=pct))
        if r["reasons"]:
            notes.append(f"{u}: " + "; ".join(tr(r["reasons"], lang)))
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


def handle_password(text, lang):
    pw = extract_password(text)
    if not pw:
        return out("check_password", t("pw_usage", lang))
    r = check_password(pw)
    status = {"weak": "bad", "medium": None, "strong": "safe"}[r["rating"]]
    notes = ""
    if r["tips"]:
        notes = t("pw_improve", lang) + "; ".join(tr(r["tips"], lang))
    return out("check_password",
               t("pw_result", lang, rating=PW_RATING[lang][r["rating"]]),
               status, notes)


def handle_scam(text, urls, lang):
    low = text.lower()
    hits = [w for w in SCAM_WORDS if re.search(r"\b" + re.escape(w) + r"\b", low)]
    if not urls and not hits and len(text.split()) < 8:
        return out("scam_message", t("scam_paste", lang))

    lines, notes, bad = [], [], False
    if urls:
        lines, notes, bad = handle_urls(urls, lang)
    if len(hits) >= 3:
        bad = True

    if bad:
        head = t("scam_bad", lang)
    elif hits:
        head = t("scam_some", lang)
    else:
        head = t("scam_none", lang)

    if hits:
        notes.append(t("scam_words", lang) + ", ".join(hits))
    return out("scam_message", "\n".join([head] + lines),
               "bad" if bad else None, " | ".join(notes))


def respond(message, history=None, allow_llm=True):
    text = message.strip()
    lang = detect_lang(text)
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
        return out(intent, t("greeting", lang))
    if intent == "about":
        return out(intent, t("about", lang))
    if intent == "creator":
        return out(intent, t("creator", lang))
    if intent == "image_request":
        return out(intent, t("image", lang))
    if intent == "thanks":
        return out(intent, t("thanks", lang))
    if intent == "check_url":
        if not urls:
            return out(intent, t("paste_link", lang))
        lines, notes, bad = handle_urls(urls, lang)
        return out(intent, "\n".join(lines), "bad" if bad else "safe", " | ".join(notes))
    if intent == "check_password":
        return handle_password(text, lang)
    if intent == "scam_message":
        return handle_scam(text, urls, lang)

    strong = answer_question(text, 0.35)
    if intent == "security_qa" and strong and lang == "en":
        return out("security_qa", strong)

    reply = ask_llm(text, history, lang) if allow_llm else None
    if reply:
        return out("llm", reply)

    if lang == "en" or intent == "security_qa":
        weak = answer_question(text, 0.12)
        if weak:
            return out("security_qa", weak)

    if not allow_llm:
        return out("unknown", t("quota_cap", lang))
    if get_last_status() == "rate_limit":
        return out("unknown", t("quota_rate", lang))
    return out("unknown", t("no_llm", lang))