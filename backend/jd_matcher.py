import re
from collections import Counter

# Common English stop words to filter out
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "must",
    "we", "you", "they", "he", "she", "it", "this", "that", "these", "those",
    "our", "your", "their", "its", "not", "no", "nor", "so", "yet", "both",
    "either", "neither", "each", "every", "all", "any", "few", "more",
    "most", "other", "some", "such", "only", "own", "same", "than", "too",
    "very", "just", "because", "if", "while", "although", "though", "since",
    "until", "unless", "about", "above", "after", "before", "between",
    "into", "through", "during", "including", "without", "across", "behind",
    "within", "along", "following", "across", "behind", "beyond", "plus",
    "except", "up", "out", "around", "down", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why", "how",
    "what", "which", "who", "whom", "whose", "work", "working", "team",
    "able", "good", "strong", "well", "also", "like", "make", "use", "using",
    "used", "new", "must", "will", "help", "join", "role", "looking", "seeking",
    "required", "preferred", "plus", "bonus", "nice", "knowledge", "understanding",
    "experience", "years", "year", "month",
}

# Curated tech/skill phrases to recognise as single tokens
_KNOWN_PHRASES = [
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "data science", "software engineering",
    "system design", "data structures", "algorithms", "object oriented",
    "functional programming", "distributed systems", "cloud computing",
    "rest api", "graphql api", "ci/cd", "continuous integration",
    "continuous deployment", "infrastructure as code", "test driven development",
    "agile methodology", "design patterns", "microservices architecture",
    "large language models", "generative ai", "prompt engineering",
    "data engineering", "data analysis", "data visualization",
    "version control", "code review",
]


def _extract_phrases(text: str) -> list[str]:
    """Pull known multi-word phrases from text before tokenising."""
    lower = text.lower()
    found = []
    for phrase in _KNOWN_PHRASES:
        if phrase in lower:
            found.append(phrase)
    return found


def _tokenise(text: str) -> list[str]:
    """Return meaningful single-word tokens from text."""
    words = re.findall(r"\b[a-z][a-z0-9\+\#\.]*\b", text.lower())
    return [w for w in words if w not in _STOP_WORDS and len(w) > 2]


def extract_jd_keywords(jd_text: str, top_n: int = 40) -> list[str]:
    """
    Extract the most relevant technical keywords and phrases from a job description.
    Returns up to *top_n* terms ranked by frequency.
    """
    phrases = _extract_phrases(jd_text)
    tokens = _tokenise(jd_text)

    # Remove words that are already captured in a phrase
    phrase_words = {w for p in phrases for w in p.split()}
    filtered_tokens = [t for t in tokens if t not in phrase_words]

    # Frequency rank single tokens, then prepend phrases (always included)
    freq = Counter(filtered_tokens)
    ranked_tokens = [w for w, _ in freq.most_common(top_n)]

    return phrases + ranked_tokens


def match_resume_with_jd(resume_text: str, jd_text: str) -> tuple[int, list[str]]:
    """
    Compare resume against job description.

    Returns:
        match_score  – 0-100 percentage of JD keywords present in resume
        missing      – list of JD keywords absent from the resume
    """
    resume_lower = resume_text.lower()

    jd_keywords = extract_jd_keywords(jd_text)
    if not jd_keywords:
        return 0, []

    matched = [kw for kw in jd_keywords if kw in resume_lower]
    missing = [kw for kw in jd_keywords if kw not in resume_lower]

    match_score = int(len(matched) / len(jd_keywords) * 100)

    # Cap missing list to the most impactful 15 terms
    return match_score, missing[:15]
