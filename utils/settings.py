import pathlib

ROOT_FOLDER = pathlib.Path(__file__).parent.parent

def load_system_prompt_text(prompt_file_name: str) -> str:
    """Load system prompt from markdown file."""
    prompt_path = ROOT_FOLDER / ".github" / "prompts" / prompt_file_name
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
