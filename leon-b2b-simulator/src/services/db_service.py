from google.cloud import bigquery
import json
import datetime

def save_simulation_to_bq(project_id: str, payload: dict):
    """
    Toma los resultados de la simulación y los guarda en BigQuery.
    Está diseñado para no romper la aplicación si la base de datos falla.
    """
    try:
        # 1. Inicializar el cliente de BigQuery
        client = bigquery.Client(project=project_id)
        
        # 2. Definir el destino exacto (Proyecto.Dataset.Tabla)
        table_id = f"{project_id}.simulator_data.evaluations"

        # 3. Formatear la fila asegurando que coincida con nuestro esquema
        row_to_insert = [
            {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "bms_id": payload.get("bms_id", "UNKNOWN"),
                "sim_mode": payload.get("sim_mode", "Unknown"),
                "target_company": payload.get("target_company", ""),
                "role": payload.get("role", ""),
                "final_score": float(payload.get("final_score", 0.0)),
                "status": payload.get("status", ""),
                "detailed_evaluation": json.dumps(payload.get("detailed_evaluation", [])),
                "transcript": payload.get("transcript", "")
            }
        ]

        # 4. Insertar los datos
        errors = client.insert_rows_json(table_id, row_to_insert)
        
        if not errors:
            print(f"✅ [BigQuery] Evaluación de {payload.get('bms_id')} guardada exitosamente.")
        else:
            print(f"❌ [BigQuery] Errores al insertar: {errors}")
            
    except Exception as e:
        print(f"❌ [BigQuery] Error crítico de conexión: {e}")
