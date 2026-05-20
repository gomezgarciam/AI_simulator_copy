import json
import logging
from unittest.mock import MagicMock, patch

from src.evaluation.rubric_engine import evaluate_transcript


@patch("src.evaluation.rubric_engine.create_rubric_feedback_prompt")
@patch("src.evaluation.rubric_engine.load_rubric_config")
def test_evaluate_transcript_with_mock_gemini(
    mock_load_rubric_config, mock_create_prompt
):
    # 1. Setup Mocks
    mock_load_rubric_config.return_value = {
        "parameters": [
            {
                "parameter": "Clarity",
                "type": "scored",
                "rubric_weight": 0.5,
                "category": "Communication",
            },
            {
                "parameter": "Technical_Accuracy",
                "type": "scored",
                "rubric_weight": 0.5,
                "category": "Content",
            },
        ]
    }
    mock_create_prompt.return_value = "This is a test prompt"

    mock_gemini_response_text = json.dumps(
        {
            "evaluations": [
                {
                    "parameter": "Clarity",
                    "rating": "Meets Expectations",
                    "evidence": "The BDR was clear.",
                },
                {
                    "parameter": "Technical_Accuracy",
                    "rating": "Partially Meets Expectations",
                    "evidence": "Minor technical error.",
                },
            ],
            "final_comment": "Good job overall.",
        }
    )

    mock_response = MagicMock()
    mock_response.text = mock_gemini_response_text

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_response

    # 2. Call the function with mocks
    transcript = "BDR: Hello, this is a test transcript."
    model_id = "gemini-test-model"
    rubric_name = "test_rubric"

    final_report = evaluate_transcript(
        transcript, mock_genai_client, model_id, rubric_name
    )

    # 3. Assertions
    mock_genai_client.models.generate_content.assert_called_once()
    assert final_report["final_score"] == 75
    assert final_report["status"] == "Pass"
    assert final_report["final_comment"] == "Good job overall."


@patch("src.evaluation.rubric_engine.create_rubric_feedback_prompt")
@patch("src.evaluation.rubric_engine.load_rubric_config")
def test_evaluate_transcript_handles_gemini_error(
    mock_load_rubric_config, mock_create_prompt
):
    # 1. Setup Mocks
    mock_load_rubric_config.return_value = {"parameters": []}
    mock_create_prompt.return_value = "This is a test prompt"

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.side_effect = ValueError(
        "Test Gemini Error"
    )

    # 2. Call the function
    final_report = evaluate_transcript(
        "transcript", mock_genai_client, "model", "rubric"
    )

    # 3. Assertions
    assert final_report["status"] == "Error"
    assert "Test Gemini Error" in final_report["error_message"]
    assert final_report["final_score"] == 0


@patch("src.evaluation.rubric_engine.create_rubric_feedback_prompt")
@patch("src.evaluation.rubric_engine.load_rubric_config")
def test_evaluate_transcript_handles_empty_gemini_response(
    mock_load_rubric_config, mock_create_prompt
):
    # 1. Setup Mocks
    mock_load_rubric_config.return_value = {"parameters": []}
    mock_create_prompt.return_value = "This is a test prompt"

    mock_response = MagicMock()
    mock_response.text = ""  # Empty text
    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_response

    # 2. Call the function
    final_report = evaluate_transcript(
        "transcript", mock_genai_client, "model", "rubric"
    )

    # 3. Assertions
    assert final_report["status"] == "Error"
    assert "Empty response from Gemini" in final_report["error_message"]
    assert final_report["final_score"] == 0


@patch("src.evaluation.rubric_engine.create_rubric_feedback_prompt")
@patch("src.evaluation.rubric_engine.load_rubric_config")
def test_evaluate_transcript_logs_error(
    mock_load_rubric_config, mock_create_prompt, caplog
):
    # 1. Setup Mocks
    mock_load_rubric_config.return_value = {"parameters": []}
    mock_create_prompt.return_value = "This is a test prompt"

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.side_effect = ValueError(
        "Logging Test Error"
    )

    # 2. Call the function
    with caplog.at_level(logging.ERROR):
        evaluate_transcript("transcript", mock_genai_client, "model", "rubric")

    # 3. Assert that the error was logged
    error_records = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_records) > 0

    error_record = error_records[0]
    assert error_record.name == "bdr_simulator"
    assert "Logging Test Error" in error_record.message
