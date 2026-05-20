import pytest

from src.evaluation.scoring_engine import compute_final_score


@pytest.fixture
def sample_rubric():
    return {
        "parameters": [
            {
                "parameter": "Clarity",
                "type": "scored",
                "rubric_weight": 0.4,
                "category": "Communication",
            },
            {
                "parameter": "Politeness",
                "type": "scored",
                "rubric_weight": 0.3,
                "category": "Professionalism",
            },
            {
                "parameter": "Mentions_Pricing",
                "type": "scored",
                "rubric_weight": 0.3,
                "category": "Sales",
            },
            {"parameter": "Rude", "type": "auto_fail", "category": "Professionalism"},
        ]
    }


def test_compute_final_score_perfect(sample_rubric):
    evaluations = [
        {"parameter": "Clarity", "rating": "Meets Expectations"},
        {"parameter": "Politeness", "rating": "Meets Expectations"},
        {"parameter": "Mentions_Pricing", "rating": "Meets Expectations"},
    ]
    result = compute_final_score(evaluations, sample_rubric)
    assert result["final_score"] == 100
    assert result["status"] == "Pass"
    assert result["auto_fail"] is False


def test_compute_final_score_mixed(sample_rubric):
    evaluations = [
        {"parameter": "Clarity", "rating": "Meets Expectations"},
        {"parameter": "Politeness", "rating": "Partially Meets Expectations"},
        {"parameter": "Mentions_Pricing", "rating": "Needs Improvement"},
    ]
    result = compute_final_score(evaluations, sample_rubric)
    # Clarity: 0.4 * 100 = 40
    # Politeness: 0.3 * 50 = 15
    # Mentions_Pricing: 0.3 * 0 = 0
    # Total actual_points = 55
    # Max possible points = 100
    # final_score = (55/100) * 100 = 55
    assert result["final_score"] == 55
    assert result["status"] == "Needs Improvement"
    assert result["auto_fail"] is False


def test_compute_final_score_with_na(sample_rubric):
    evaluations = [
        {"parameter": "Clarity", "rating": "Meets Expectations"},
        {"parameter": "Politeness", "rating": "N/A"},
        {"parameter": "Mentions_Pricing", "rating": "Meets Expectations"},
    ]
    result = compute_final_score(evaluations, sample_rubric)
    # Max possible points is now (0.4 * 100) + (0.3 * 100) = 70
    # Actual points is (0.4 * 100) + (0.3 * 100) = 70
    # final_score = (70/70) * 100 = 100
    assert result["final_score"] == 100
    assert result["status"] == "Pass"
    assert result["max_points"] == 70


def test_compute_final_score_auto_fail(sample_rubric):
    evaluations = [
        {"parameter": "Clarity", "rating": "Meets Expectations"},
        {"parameter": "Politeness", "rating": "Meets Expectations"},
        {"parameter": "Rude", "rating": "Auto-Fail"},
    ]
    result = compute_final_score(evaluations, sample_rubric)
    assert result["final_score"] == 0
    assert result["status"] == "Fail (Auto-Fail)"
    assert result["auto_fail"] is True


def test_compute_final_score_empty_evaluations(sample_rubric):
    evaluations = []
    result = compute_final_score(evaluations, sample_rubric)
    assert result["final_score"] == 100
    assert result["status"] == "Pass"
    assert result["actual_points"] == 0
    assert result["max_points"] == 0


def test_compute_final_score_all_na(sample_rubric):
    evaluations = [
        {"parameter": "Clarity", "rating": "N/A"},
        {"parameter": "Politeness", "rating": "N/A"},
        {"parameter": "Mentions_Pricing", "rating": "N/A"},
    ]
    result = compute_final_score(evaluations, sample_rubric)
    assert result["final_score"] == 100
    assert result["status"] == "Pass"
    assert result["max_points"] == 0
    assert result["actual_points"] == 0
