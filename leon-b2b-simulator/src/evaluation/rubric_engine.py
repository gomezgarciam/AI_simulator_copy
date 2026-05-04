import json
import logging
from typing import Dict, Any, List
from src.prompts.rubric_feedback_prompt import create_rubric_feedback_prompt
from src.evaluation.rubric_config import load_rubric_config
from src.evaluation.scoring_engine import compute_final_score

logger = logging.getLogger("rubric_engine")

def evaluate_transcript(transcript: str, genai_client: Any, model_id: str, rubric_name: str) -> Dict[str, Any]:
    """
    Orchestrates the evaluation process:
    1. Loads the rubric.
    2. Calls Gemini for qualitative evaluation.
    3. Computes the final score using the scoring engine.
    """
    try:
        # 1. Load Rubric
        rubric_config = load_rubric_config(rubric_name)
        
        # 2. Prepare Prompt
        prompt = create_rubric_feedback_prompt(transcript, rubric_name)
        
        # 3. Call Gemini
        logger.info("Calling Gemini for rubric evaluation...")
        response = genai_client.models.generate_content(
            model=model_id,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2, # Lower temperature for consistency
            }
        )
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini during evaluation.")
            
        qualitative_eval = json.loads(response.text)
        evaluations = qualitative_eval.get("evaluations", [])
        final_comment = qualitative_eval.get("final_comment", "")
        
        # 4. Compute Quantitative Score
        logger.info("Computing final scores with scoring engine...")
        final_report = compute_final_score(evaluations, rubric_config)
        
        # 5. Add final comment from Gemini
        final_report["final_comment"] = final_comment
        
        return final_report

    except Exception as e:
        logger.error(f"Error in evaluate_transcript: {e}")
        return {
            "status": "Error",
            "error_message": str(e),
            "final_score": 0,
            "evaluations": [],
            "final_comment": "An error occurred during evaluation."
        }

def format_transcript_from_messages(messages: List[Dict[str, str]]) -> str:
    """
    Converts session messages into a clean text transcript.
    """
    transcript = ""
    for msg in messages:
        role = "BDR" if msg["role"] == "user" else "Alex (Prospect)"
        content = msg["content"]
        transcript += f"{role}: {content}\n"
    return transcript