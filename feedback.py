"""Customer feedback: sentiment (VADER) + theme tagging."""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

THEMES = {
    "Delivery": ["deliver", "ship", "late", "delay", "arriv"],
    "Pricing": ["price", "pricing", "expensive", "value", "cost"],
    "Support": ["support", "agent", "refund", "service"],
    "Quality": ["quality", "defect", "damag", "broken", "reliab"],
    "Ease of use": ["easy", "app", "interface", "setup", "confusing"],
}


def analyze(fb):
    if fb.empty:  # nothing to analyze, but keep the same columns
        return fb.assign(score=[], label=[], **{t: [] for t in THEMES})
    sia = SentimentIntensityAnalyzer()
    fb["score"] = fb.text.apply(lambda t: sia.polarity_scores(t)["compound"])
    fb["label"] = fb.score.apply(lambda s: "positive" if s >= 0.05 else "negative" if s <= -0.05 else "neutral")
    for theme, words in THEMES.items():
        fb[theme] = fb.text.str.lower().str.contains("|".join(words))
    return fb