import json
import pandas as pd
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


def json_to_dataframe(raw_json: str, debug: bool = False) -> pd.DataFrame | None:
    """Convert a JSON string to a DataFrame, if possible."""
    try:
        parsed = json.loads(raw_json)
    except Exception:
        return None

    if isinstance(parsed, dict) and parsed.get("success") is False:
        return None

    data = parsed.get("data") if isinstance(parsed, dict) and "data" in parsed else parsed

    if isinstance(data, list):
        col = "date" if data and isinstance(data[0], str) and "-" in data[0] else "value"
        return pd.DataFrame({col: data})

    if isinstance(data, dict):
        list_items = [(k, v) for k, v in data.items() if isinstance(v, list)]
        if list_items:
            lengths = [len(v) for _, v in list_items]
            if len(set(lengths)) == 1:
                n_rows = lengths[0]
                records = [{k: v[i] for k, v in list_items} for i in range(n_rows)]
                df = pd.DataFrame(records)
                # Add scalar metadata from the data object.
                for mk, mv in data.items():
                    if mk not in dict(list_items) and not isinstance(mv, list):
                        df[mk] = mv
                # Add scalar metadata from the outer payload.
                if isinstance(parsed, dict):
                    for mk, mv in parsed.items():
                        if mk != "data" and not isinstance(mv, (dict, list)):
                            df[mk] = mv
                return df
    
    # Extract & debug nested
    nested_key = next((k for k in ['data', 'records'] if k in data), None)
    if nested_key:
        nested = data[nested_key]
        if debug: print(f"Processing {nested_key}:", nested.keys())
        
        list_items = [(k, nested[k]) for k in nested if isinstance(nested[k], list)]
        if debug: print("Lists found:", len(list_items), [k for k,_ in list_items])
        
        if len(list_items) >= 1:
            lengths = [len(v) for _,v in list_items]
            if debug: print("Lengths:", lengths, "Uniform?", len(set(lengths)) == 1)
            
            if len(set(lengths)) == 1:
                n_rows = lengths[0]
                records = [{k: v[i] for k,v in list_items} for i in range(n_rows)]
                df = pd.DataFrame(records)
                # Metadata cols
                for mk in data:
                    if mk != nested_key:
                        df[mk] = data[mk]
                if debug: print(f"SUCCESS: {n_rows}x{len(list_items)}")
                return df
    
    # Fallback
    df = pd.json_normalize(data)
    if debug: print("Fallback shape:", df.shape)
    return df