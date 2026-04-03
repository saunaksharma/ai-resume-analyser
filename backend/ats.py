import re


# ── Keyword taxonomy ──────────────────────────────────────────────────────────
KEYWORD_CATEGORIES = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "swift", "kotlin", "scala", "r", "matlab", "php", "bash", "sql",
        "html", "css", "dart", "perl", "lua",
    ],
    "frameworks_backend": [
        "fastapi", "flask", "django", "spring", "express", "rails", "laravel",
        "gin", "fiber", "nestjs", "actix", "grpc", "graphql", "rest api",
        "microservices", "serverless",
    ],
    "frameworks_frontend": [
        "react", "vue", "angular", "svelte", "nextjs", "nuxtjs", "gatsby",
        "tailwind", "bootstrap", "redux", "webpack",
    ],
    "data_ml": [
        "machine learning", "deep learning", "neural network", "nlp",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "pandas", "numpy", "spark", "hadoop", "etl", "data pipeline",
        "feature engineering", "model training", "llm", "transformers",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "circleci", "helm", "prometheus", "grafana",
        "ci/cd", "infrastructure as code", "iac",
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "sqlite", "neo4j", "snowflake", "bigquery",
        "oracle", "sql server",
    ],
    "practices": [
        "agile", "scrum", "kanban", "tdd", "bdd", "code review",
        "unit testing", "integration testing", "api design", "system design",
        "design patterns", "solid", "dry", "clean code",
    ],
}

ALL_KEYWORDS = [kw for kws in KEYWORD_CATEGORIES.values() for kw in kws]

# Section header patterns
SECTION_PATTERNS = {
    "contact":    r"\b(email|phone|linkedin|github|portfolio|address|contact)\b",
    "summary":    r"\b(summary|objective|profile|about me|overview)\b",
    "experience": r"\b(experience|work history|employment|career|internship|intern)\b",
    "education":  r"\b(education|degree|university|college|bachelor|master|phd|b\.tech|m\.tech)\b",
    "skills":     r"\b(skills|technologies|tech stack|proficiencies|competencies)\b",
    "projects":   r"\b(projects|portfolio|open.?source|github)\b",
    "certifications": r"\b(certifications?|certificates?|courses?|credentials?)\b",
    "achievements": r"\b(achievements?|awards?|honors?|recognition)\b",
}

QUANTIFIER_PATTERN = re.compile(
    r"(\d+[\.,]?\d*\s*(%|percent|x|times|users?|customers?|requests?|"
    r"ms|seconds?|hours?|days?|weeks?|months?|years?|k\b|m\b|million|billion|"
    r"\$|usd|eur|gbp|inr))",
    re.IGNORECASE,
)

ACTION_VERBS = [
    "built", "developed", "designed", "implemented", "deployed", "led",
    "managed", "created", "engineered", "architected", "optimized", "improved",
    "reduced", "increased", "automated", "scaled", "launched", "delivered",
    "collaborated", "mentored", "researched", "analyzed", "integrated",
    "migrated", "refactored", "contributed",
]


def detect_sections(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {section: bool(re.search(pat, lower))
            for section, pat in SECTION_PATTERNS.items()}


def calculate_ats_score(text: str) -> tuple[int, list[str], dict]:
    lower = text.lower()
    score = 0
    details = []
    section_scores: dict[str, int] = {}

    # ── 1. Keyword coverage (0–30 pts) ──────────────────────────────────────
    found_keywords = [kw for kw in ALL_KEYWORDS if kw in lower]
    keyword_score = min(len(found_keywords) * 2, 30)
    score += keyword_score
    details.append(f"Keyword coverage: {len(found_keywords)} keywords found (+{keyword_score})")
    section_scores["Keywords"] = keyword_score

    # ── 2. Section structure (0–20 pts) ─────────────────────────────────────
    sections = detect_sections(text)
    core_sections = ["contact", "experience", "education", "skills"]
    present = sum(1 for s in core_sections if sections.get(s))
    struct_score = present * 5  # 5 pts each
    score += struct_score
    present_names = [s for s in core_sections if sections.get(s)]
    missing_names = [s for s in core_sections if not sections.get(s)]
    details.append(
        f"Resume structure: {present}/4 core sections present (+{struct_score})"
        + (f" — missing: {', '.join(missing_names)}" if missing_names else "")
    )
    section_scores["Structure"] = struct_score

    # ── 3. Quantified achievements (0–20 pts) ───────────────────────────────
    quant_matches = QUANTIFIER_PATTERN.findall(lower)
    quant_score = min(len(quant_matches) * 4, 20)
    score += quant_score
    details.append(
        f"Quantified achievements: {len(quant_matches)} metrics found (+{quant_score})"
    )
    section_scores["Achievements"] = quant_score

    # ── 4. Action verbs (0–15 pts) ───────────────────────────────────────────
    verbs_found = [v for v in ACTION_VERBS if v in lower]
    verb_score = min(len(verbs_found) * 3, 15)
    score += verb_score
    details.append(
        f"Action verbs: {len(verbs_found)} found (+{verb_score})"
    )
    section_scores["Action Verbs"] = verb_score

    # ── 5. Bonus sections (0–15 pts) ────────────────────────────────────────
    bonus_sections = ["projects", "certifications", "achievements", "summary"]
    bonus_present = [s for s in bonus_sections if sections.get(s)]
    bonus_score = min(len(bonus_present) * 4, 15)
    if bonus_present:
        score += bonus_score
        details.append(
            f"Bonus sections ({', '.join(bonus_present)}) (+{bonus_score})"
        )
    section_scores["Bonus Sections"] = bonus_score

    score = min(score, 100)

    return score, details, section_scores
