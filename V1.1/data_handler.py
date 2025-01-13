# data_handler.py
import json
import os
from typing import Dict, Any, List

def load_character_dna(filepath: str) -> Dict[str, Any]:
    """Loads character's DNA from a JSON or JSONL file."""
    if os.path.exists(filepath):
        try:
           if filepath.endswith(".jsonl"):
                with open(filepath, 'r') as f:
                  for line in f:
                     return json.loads(line)
           else:
              with open(filepath, 'r') as f:
                  return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filepath}. Ensure it's valid JSON/JSONL.")
            return {}
    return {}

def save_character_dna(filepath: str, data: Dict[str, Any]):
    """Saves character's DNA to a JSON or JSONL file."""
    if filepath.endswith(".jsonl"):
        with open(filepath, 'w') as f:
            json.dump(data, f, default=str) # Added default=str for datetime
            f.write('\n')
    else:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4, default=str) # Added default=str for datetime

def save_json(filepath: str, data: Any):
    """Saves data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, default=str) # Added default=str for datetime

def load_json(filepath: str) -> Any:
    """Loads data from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def load_supporting_characters(directory: str) -> Dict[str, Dict[str, Any]]:
    """Loads all supporting characters from JSON files in the specified directory."""
    characters = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            char_data = load_character_dna(filepath)
            if char_data and 'name' in char_data:
               characters[char_data['name']] = char_data
    return characters