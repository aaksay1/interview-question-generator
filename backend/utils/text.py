import re

def clean_text(text: str) -> str:
    """
    Cleans extracted text by removing extra spaces and newlines.
    """
    text = re.sub(r'\n+', '\n', text)     # collapse multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)   # collapse spaces/tabs
    return text.strip()