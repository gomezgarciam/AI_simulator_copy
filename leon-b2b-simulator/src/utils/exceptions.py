from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.utils.logger import logger


class BDRSimulatorError(Exception):
    """Base exception for the BDR Simulator."""

    pass


class AIServiceError(BDRSimulatorError):
    """Raised when an AI service (Gemini, STT, TTS) fails."""

    pass


class DatabaseError(BDRSimulatorError):
    """Raised when BigQuery operations fail."""

    pass


class AudioProcessingError(BDRSimulatorError):
    """Raised when audio conversion or loading fails."""

    pass


# Retry decorator for AI Services
ai_service_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((AIServiceError, Exception)),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying AI service call (attempt {retry_state.attempt_number})..."
    ),
)
