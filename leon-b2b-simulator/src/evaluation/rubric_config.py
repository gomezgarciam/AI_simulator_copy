import json
import os

def load_rubric_config(file_path=None):
    if file_path is None:
        # Default local path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = os.path.join(base_dir, "config", "rubrics", "bdr_qa_rubric_v1.json")
    
    with open(file_path, 'r') as f:
        return json.load(f)