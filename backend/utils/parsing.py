"""
JSON extraction utilities for parsing LLM responses.

LLM responses may contain JSON wrapped in markdown code blocks or as plain JSON.
This module handles various formats and extracts the questions array.
"""
import json
import re


def extract_questions(response: str) -> list:
    """
    Extracts JSON array of questions from LLM response.
    
    Handles multiple formats:
    1. JSON wrapped in ```json ... ``` code blocks
    2. JSON array anywhere in the response
    3. Plain JSON response
    4. JSON object with "questions" key
    
    Args:
        response: LLM response string (may contain JSON)
        
    Returns:
        List of question dictionaries: [{"category": "...", "question": "..."}, ...]
        Returns empty list if no valid JSON found
    """
    if not response or not response.strip():
        return []

    # Try to find JSON wrapped in code blocks first (most common format)
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
        # If it's a list, return it
        if isinstance(parsed, list):
            return parsed
        # If it's a dict, try to extract a list from it
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
