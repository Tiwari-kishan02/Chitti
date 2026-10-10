import re
from urllib.parse import urlparse

KEYWORDS = ["login", "verify", "secure", "account", "update", "bank",
            "paypal", "signin", "confirm", "password", "webscr", "ebay"]
COMMON_TLDS = {"com", "org", "net", "edu", "gov", "in", "io", "co", "uk", "de"}
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def extract_features(url):
    url = re.sub(r"^https?://", "", str(url).strip())
    try:
        parsed = urlparse("http://" + url)
        host = parsed.netloc.lower()
        path = parsed.path
        query = parsed.query
    except ValueError:
        host, path, query = "", "", ""

    host_only = host.split(":")[0]
    tld = host_only.split(".")[-1]
    lower = url.lower()
    digits = sum(c.isdigit() for c in url)
    host_digits = sum(c.isdigit() for c in host_only)

    return {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "dots": url.count("."),
        "hyphens": url.count("-"),
        "host_hyphens": host_only.count("-"),
        "host_digits": host_digits,
        "underscores": url.count("_"),
        "slashes": url.count("/"),
        "digits": digits,
        "digit_ratio": digits / max(len(url), 1),
        "question_marks": url.count("?"),
        "equals": url.count("="),
        "ampersands": url.count("&"),
        "at_symbol": url.count("@"),
        "percent": url.count("%"),
        "subdomains": max(host_only.count(".") - 1, 0),
        "has_ip": int(bool(IP_PATTERN.match(host_only))),
        "has_port": int(":" in host),
        "keyword_count": sum(k in lower for k in KEYWORDS),
        "host_keyword_count": sum(k in host_only for k in KEYWORDS),
        "has_php": int(".php" in lower),
        "has_exe": int(".exe" in lower),
        "tld_length": len(tld),
        "common_tld": int(tld in COMMON_TLDS),
    }