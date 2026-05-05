import json
import os

RUBRIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../config/rubrics")

def load_rubric_config(rubric_name: str) -> dict:
    """
    Loads the rubric configuration from a specified JSON file.
    """
    file_path = os.path.join(RUBRIC_DIR, f"{rubric_name}.json")
    
    with open(file_path, 'r') as f:
        return json.load(f)