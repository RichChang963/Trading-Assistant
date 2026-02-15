import pathlib
import re
import pycountry

ROOT_FOLDER = pathlib.Path(__file__).parent.parent

def load_system_prompt_text(prompt_file_name: str) -> str:
    """Load a system prompt from a markdown file.

    Parameters
    ----------
    prompt_file_name : str
        Markdown filename containing the prompt.

    Returns
    -------
    str
        Prompt text loaded from disk.
    """
    prompt_path = ROOT_FOLDER / ".github" / "prompts" / prompt_file_name
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()



def resolve_country_from_query(raw_query: str) -> str | None:
    words = re.findall(r"[a-zA-Z]+", raw_query)
    if not words:
        return None

    alias_map = {
        "usa": "USA",
        "us": "USA",
        "united states": "USA",
        "united states of america": "USA",
        "uk": "GBR",
        "united kingdom": "GBR",
        "great britain": "GBR",
    }

    query_text = " ".join(words).lower()
    if query_text in alias_map:
        return alias_map[query_text]

    # Prefer phrases that follow common prepositions (e.g., "in Germany").
    match = re.search(r"\b(?:in|for|of)\s+([A-Za-z\s]+)", raw_query)
    if match:
        candidate = match.group(1).strip()
        candidate_lower = candidate.lower()
        if candidate_lower in alias_map:
            return alias_map[candidate_lower]
        try:
            return pycountry.countries.lookup(candidate).alpha_3
        except Exception:
            pass

    stopwords = {
        "what",
        "does",
        "recent",
        "interest",
        "rate",
        "rates",
        "look",
        "like",
        "show",
        "me",
        "the",
        "a",
        "an",
        "in",
        "for",
        "of",
        "to",
        "and",
    }

    # Try longest phrases first (3-word down to 1-word), skipping stopwords.
    for size in (3, 2, 1):
        for i in range(len(words) - size + 1):
            candidate_words = words[i:i + size]
            candidate_lower = " ".join(w.lower() for w in candidate_words)
            if any(w.lower() in stopwords for w in candidate_words):
                continue
            if candidate_lower in alias_map:
                return alias_map[candidate_lower]
            candidate = " ".join(candidate_words)
            if len(candidate) == 3 and candidate.isalpha():
                return candidate.upper()
            try:
                return pycountry.countries.lookup(candidate).alpha_3
            except Exception:
                continue

    return None
