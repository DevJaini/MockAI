import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text, top_n=25):
    # Clean up text
    clean_text = re.sub(r"[^\w\s]", " ", text.lower())
    clean_text = re.sub(r"\d+", "", clean_text)

    # Run spaCy to get POS tags
    doc = nlp(clean_text)
    allowed_tokens = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN", "ADJ") and len(token.text) > 2]

    # Re-join filtered tokens into a TF-IDF input
    filtered_text = " ".join(allowed_tokens)

    # TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([filtered_text])
    scores = X.toarray()[0]
    keywords = vectorizer.get_feature_names_out()

    # Return top N keywords by score
    keyword_scores = sorted(zip(keywords, scores), key=lambda x: x[1], reverse=True)
    return [kw for kw, score in keyword_scores[:top_n]]