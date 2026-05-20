from typing import Any, Dict, List


def compute_final_score(
    evaluations: List[Dict[str, Any]], rubric_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes the final score based on Gemini's ratings and the rubric configuration.
    """
    params_map = {p["parameter"]: p for p in rubric_config["parameters"]}

    actual_points = 0.0
    # Pre-calculate max points from all 'scored' parameters in the rubric
    max_possible_points = sum(
        p.get("rubric_weight", 0) * 100
        for p in rubric_config.get("parameters", [])
        if p.get("type") == "scored"
    )

    has_auto_fail = False
    detailed_evaluations = []

    # Create a map of evaluated parameters for efficient lookup
    evals_map = {e["parameter"]: e for e in evaluations}

    # Iterate over the rubric parameters to ensure all are accounted for
    for param_name, param_config in params_map.items():
        weight = param_config.get("rubric_weight", 0)
        category = param_config.get("category", "Unknown")

        # Get the evaluation for the current parameter, if it exists
        eval_item = evals_map.get(param_name)

        rating = eval_item.get("rating", "N/A") if eval_item else "N/A"
        evidence = eval_item.get("evidence", "") if eval_item else ""
        improvement_tip = eval_item.get("improvement_tip", "") if eval_item else ""
        points = 0.0

        # Handle auto-fail condition
        if param_config.get("type") == "auto_fail" and rating == "Auto-Fail":
            has_auto_fail = True

        # Adjust max points for N/A ratings
        if rating == "N/A" and param_config.get("type") == "scored":
            max_possible_points -= weight * 100
            points = 0.0
        elif rating == "Meets Expectations":
            points = weight * 100
            actual_points += points
        elif rating == "Partially Meets Expectations":
            points = weight * 50
            actual_points += points
        # For "Needs Improvement", points remain 0

        detailed_evaluations.append(
            {
                "category": category,
                "parameter": param_name,
                "rating": rating,
                "weight": weight,
                "points": round(points, 2),
                "evidence": evidence,
                "improvement_tip": improvement_tip,
            }
        )

    if has_auto_fail:
        final_score = 0
        status = "Fail (Auto-Fail)"
        actual_points = 0  # If auto-fail, score is 0
    else:
        if max_possible_points > 0:
            final_score = round((actual_points / max_possible_points) * 100)
        else:
            # Handle case where all items are N/A or not scored
            final_score = 100 if actual_points == 0 else 0

        status = "Pass" if final_score >= 70 else "Needs Improvement"

    return {
        "status": status,
        "final_score": final_score,
        "actual_points": round(actual_points, 2),
        "max_points": round(max_possible_points, 2),
        "auto_fail": has_auto_fail,
        "evaluations": detailed_evaluations,
    }
