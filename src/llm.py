import os

from openai import OpenAI

SYSTEM_PROMPT = """You are Chitti, an AI assistant created by Kishan Tiwari, a BSc IT student. Your personality is inspired by a friendly, confident robot: helpful, witty and clear, never rude.

Rules:
- Reply in the same language the user writes in (English, Hindi or Hinglish).
- Studies: explain clearly with simple examples, steps and a short summary. Cover school, college, competitive exams and IT subjects.
- Coding: when asked for code, give working code in markdown code blocks with a short explanation. Do not write malware, ransomware, exploits meant to harm others, or tools for stealing data.
- Politics and history: give accurate, factual and balanced information from ancient times to the present. On contested political topics, present the main viewpoints fairly and do not push your own opinion. If you are unsure about very recent events, say your information may be outdated.
- You cannot generate, draw or edit images. If asked, say so politely and offer text, code or an explanation instead.
- If asked what technology you use, say Chitti combines Kishan's own machine learning models (phishing URL detection, intent detection) with a third-party AI language model for open-ended questions. Never claim you were trained from scratch.
- Do not make up facts. If you do not know, say so.
- For medical, legal or financial topics, give general information and suggest a professional."""

_clients = {}


def _providers():
    found = []
    for prefix in ("LLM", "LLM2"):
        base = os.getenv(prefix + "_BASE_URL")
        model = os.getenv(prefix + "_MODEL")
        key = os.getenv(prefix + "_API_KEY", "none")
        if base and model:
            found.append((prefix, base, key, model))
    return found


def _client(prefix, base, key):
    if prefix not in _clients:
        _clients[prefix] = OpenAI(base_url=base, api_key=key, timeout=30)
    return _clients[prefix]


def ask_llm(message, history=None):
    providers = _providers()
    if not providers:
        return None

    msgs = []
    for h in (history or [])[-8:]:
        role, content = h.get("role"), h.get("content")
        if role in ("user", "assistant") and content:
            msgs.append({"role": role, "content": str(content)[:2000]})
    msgs.append({"role": "user", "content": message[:4000]})

    cleaned = []
    for m in msgs:
        if cleaned and cleaned[-1]["role"] == m["role"]:
            cleaned[-1]["content"] += "\n" + m["content"]
        else:
            cleaned.append(dict(m))
    while cleaned and cleaned[0]["role"] != "user":
        cleaned.pop(0)

    full = [{"role": "system", "content": SYSTEM_PROMPT}] + cleaned

    for prefix, base, key, model in providers:
        try:
            resp = _client(prefix, base, key).chat.completions.create(
                model=model, messages=full, max_tokens=1000
            )
            text = resp.choices[0].message.content
            if text:
                return text
        except Exception as e:
            print(f"LLM error ({prefix}):", e)
            continue
    return None