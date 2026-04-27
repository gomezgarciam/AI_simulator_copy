from typing import List, Dict, Any

def compute_final_score(evaluations: List[Dict[str, Any]], rubric_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes the final score based on Gemini's ratings and the rubric configuration.
    
    Expected format of evaluations from rubric_engine:
    [
      {
        "parameter": "Engagement",
        "rating": "Meets Expectations",
        "evidence": "...",
        "improvement_tip": "..."
      },
      ...
    ]
    """
    params_map = {p["parameter"]: p for p in rubric_config["parameters"]}
    
    actual_points = 0.0
    max_possible_points = 0.0
    has_auto_fail = False
    
    detailed_evaluations = []
    
    for eval_item in evaluations:
        param_name = eval_item["parameter"]
        rating = eval_item["rating"]
        
        if param_name not in params_map:
            continue
            
        param_config = params_map[param_name]
        weight = param_config["rubric_weight"]
        category = param_config["category"]
        
        points = 0.0
        
        if rating == "Auto-Fail":
            has_auto_fail = True
            points = 0.0
        elif rating == "Meets Expectations":
            points = weight * 100
            actual_points += points
            max_possible_points += (weight * 100)
        elif rating == "Partially Meets Expectations":
            points = weight * 50
            actual_points += points
            max_possible_points += (weight * 100)
        elif rating == "Needs Improvement":
            points = 0.0
            actual_points += points
            max_possible_points += (weight * 100)
        elif rating == "N/A":
            # Excluded from both actual and max
            points = 0.0
        
        detailed_evaluations.append({
            "category": category,
            "parameter": param_name,
            "rating": rating,
            "weight": weight,
            "points": round(points, 2),
            "evidence": eval_item.get("evidence", ""),
            "improvement_tip": eval_item.get("improvement_tip", "")
        })

    if has_auto_fail:
        final_score = 0
        status = "Fail (Auto-Fail)"
    else:
        final_score = round((actual_points / max_possible_points * 100), 2) if max_possible_points > 0 else 0
        status = "Pass" if final_score >= 70 else "Needs Improvement" # Assuming 70 is pass

    return {
        "status": status,
        "final_score": final_score,
        "actual_points": round(actual_points, 2),
        "max_points": round(max_possible_points, 2),
        "auto_fail": has_auto_fail,
        "evaluations": detailed_evaluations
    }