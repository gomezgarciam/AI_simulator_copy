from google.cloud import bigquery
import json
import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from src.config.settings import settings
from src.utils.logger import logger
from src.utils.exceptions import DatabaseError

class SimulationResult(BaseModel):
    """
    Schema validation for simulation results.
    """
    bms_id: str = Field(default="UNKNOWN")
    sim_mode: str = Field(default="Unknown")
    target_company: str = Field(default="")
    role: str = Field(default="")
    final_score: float = Field(default=0.0)
    status: str = Field(default="")
    detailed_evaluation: List[Dict[str, Any]] = Field(default_factory=list)
    transcript: str = Field(default="")
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

def save_simulation_to_bq(payload: Dict[str, Any]) -> bool:
    """
    Saves simulation results to BigQuery with logging and validation.
    """
    try:
        # Validate
        result = SimulationResult(**payload)
        
        client = bigquery.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        table_id = f"{settings.GOOGLE_CLOUD_PROJECT}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE}"

        row_to_insert = [
            {
                "timestamp": result.timestamp.isoformat(),
                "bms_id": result.bms_id,
                "sim_mode": result.sim_mode,
                "target_company": result.target_company,
                "role": result.role,
                "final_score": result.final_score,
                "status": result.status,
                "detailed_evaluation": json.dumps(result.detailed_evaluation),
                "transcript": result.transcript
            }
        ]

        errors = client.insert_rows_json(table_id, row_to_insert)
        
        if not errors:
            logger.info(f"Successfully saved simulation for BMS ID: {result.bms_id}")
            return True
        else:
            logger.error(f"BigQuery insertion errors: {errors}")
            return False
            
    except Exception as e:
        logger.error(f"Critical error saving to BigQuery: {e}")
        # We don't raise here to avoid crashing the main app flow
        return False
