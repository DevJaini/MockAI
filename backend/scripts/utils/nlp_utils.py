import re
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

# Load spaCy model with fallback download if missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str, top_n: int = 25) -> list:
    """
    Extracts top N keywords from the given text using spaCy POS filtering and TF-IDF scoring.

    Args:
        text (str): Input document.
        top_n (int): Number of top keywords to return.

    Returns:
        List[str]: Top N keywords ranked by TF-IDF.
    """
    # Basic cleanup
    clean_text = re.sub(r"[^\w\s]", " ", text.lower())
    clean_text = re.sub(r"\d+", "", clean_text)

    # POS tagging with spaCy
    doc = nlp(clean_text)
    tokens = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN", "ADJ") and len(token.text) > 2]

    if not tokens:
        return []

    filtered_text = " ".join(tokens)

    # TF-IDF scoring
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([filtered_text])
    scores = X.toarray()[0]
    keywords = vectorizer.get_feature_names_out()

    # Rank and return top keywords
    keyword_scores = sorted(zip(keywords, scores), key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in keyword_scores[:top_n]]
