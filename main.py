import requests
import time
from bs4 import BeautifulSoup

# -------------------------
# FETCH
# -------------------------
def fetch_site(url):
    start_time = time.time()
    response = requests.get(
        url,
        headers={"User-Agent": "AI-Fetcher"},
        timeout=10
    )
    return {
        "status_code": response.status_code,
        "time_taken": round(time.time() - start_time, 2),
        "html": response.text
    }

# -------------------------
# PARSING
# -------------------------
def extract_ai_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def signal_ratio(html, text):
    return round((len(text) / len(html)) * 100, 2) if html else 0

def js_dominance(html):
    soup = BeautifulSoup(html, "lxml")
    return {
        "script_count": len(soup.find_all("script")),
        "text_length": len(soup.get_text(strip=True))
    }

def heading_structure(html):
    soup = BeautifulSoup(html, "lxml")
    return {
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2"))
    }

def detect_walls(text):
    keywords = [
        "accept cookies",
        "log in",
        "sign up",
        "enable javascript",
        "agree & continue"
    ]
    text = text.lower()
    return [k for k in keywords if k in text]

# -------------------------
# SCORING
# -------------------------
def score_accessibility(status):
    return 20 if status == 200 else 10 if status in (301, 302) else 0

def score_speed(ttfb):
    if ttfb < 0.5: return 20
    if ttfb < 1.5: return 15
    if ttfb < 3: return 8
    return 0

def score_signal_ratio(ratio):
    if ratio > 25: return 20
    if ratio > 15: return 15
    if ratio > 5: return 8
    if ratio > 1: return 4
    return 0

def score_js_dependency(script_count):
    if script_count < 5: return 20
    if script_count < 15: return 12
    if script_count < 30: return 6
    return 0

def score_structure(h1, h2):
    if h1 >= 1 and h2 >= 3: return 20
    if h1 >= 1: return 10
    return 0

# -------------------------
# REPORTING
# -------------------------
def lost_points_report(scores):
    return {k: 20 - v for k, v in scores.items()}

def fix_suggestions(ratio, script_count, h1, h2, ttfb):
    fixes = []

    if ratio < 5:
        fixes.append("Move main content into server-rendered HTML.")
    if script_count > 15:
        fixes.append("Reduce JavaScript or use SSR.")
    if h1 == 0:
        fixes.append("Add one clear <h1> tag.")
    if h2 < 3:
        fixes.append("Add more <h2> subheadings.")
    if ttfb > 1.5:
        fixes.append("Improve server speed using caching/CDN.")

    return fixes

# -------------------------
# PIPELINE (THIS IS THE PRODUCT CORE)
# -------------------------
def analyze_site(url):
    data = fetch_site(url)
    ai_text = extract_ai_text(data["html"])

    ratio = signal_ratio(data["html"], ai_text)
    js_info = js_dominance(data["html"])
    headings = heading_structure(data["html"])
    walls = detect_walls(ai_text)

    scores = {
        "Accessibility": score_accessibility(data["status_code"]),
        "Speed": score_speed(data["time_taken"]),
        "Signal Quality": score_signal_ratio(ratio),
        "JavaScript Dependency": score_js_dependency(js_info["script_count"]),
        "Structure": score_structure(
            headings["h1_count"], headings["h2_count"]
        )
    }

    total_score = sum(scores.values())

    return {
        "fetch": data,
        "ratio": ratio,
        "js": js_info,
        "headings": headings,
        "walls": walls,
        "scores": scores,
        "total_score": total_score,
        "losses": lost_points_report(scores),
        "fixes": fix_suggestions(
            ratio,
            js_info["script_count"],
            headings["h1_count"],
            headings["h2_count"],
            data["time_taken"]
        )
    }

# -------------------------
# RUN (ONLY FOR CLI TESTING)
# -------------------------
if __name__ == "__main__":
    url = "https://www.facebook.com/"
    result = analyze_site(url)

    print("\nAI READABILITY SCORE:", result["total_score"], "/ 100")

    print("\nPOINTS LOST:")
    for k, v in result["losses"].items():
        if v > 0:
            print(f"- {k}: -{v}")

    print("\nRECOMMENDED FIXES:")
    for f in result["fixes"]:
        print("✔", f)