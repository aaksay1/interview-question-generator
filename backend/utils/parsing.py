import json
import re

def extract_questions(response: str):
    """
    Extracts JSON from Groq LLM response that may be wrapped in ```json ... ```
    Returns a Python list of questions.
    """
    if not response or not response.strip():
        return []

    # Try to find JSON wrapped in code blocks first
    match = re.search(r"```json\s*(\[.*?\])\s*```", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON array anywhere in the response
    match = re.search(r"(\[.*?\])", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Fallback: try parsing the whole response as JSON
    try:
        parsed = json.loads(response.strip())
        # If it's a list, return it; if it's a dict, try to extract a list from it
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict) and "questions" in parsed:
            return parsed["questions"]
        elif isinstance(parsed, dict):
            # Try to find any list value in the dict
            for value in parsed.values():
                if isinstance(value, list):
                    return value
    except json.JSONDecodeError:
        pass
    
    # If all else fails, return empty list
    return []
