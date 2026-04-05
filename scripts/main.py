import time
import pandas as pd
from sqlalchemy import create_engine
from scripts.transform import transform
from scripts.load_data import load
from scripts.utils import retry
from scripts.logger import get_logger
from prometheus_client import start_http_server, Counter, Gauge, Histogram
from scripts.config_loader import get_source_db_url

logger = get_logger()

# Metrics Prometheus
rows_extracted = Counter("rows_extracted_total", "Total des lignes extraites")
rows_transformed = Counter("rows_transformed_total", "Total des lignes transformées")
rows_loaded = Counter("rows_loaded_total", "Total des lignes chargées")
pipeline_status = Gauge("pipeline_status", "Statut du pipeline")
data_size = Gauge("data_size_rows", "Volume traité")
pipeline_duration = Histogram("pipeline_duration_seconds", "La durée du pipeline")

# Start metrics server
start_http_server(8000)

@pipeline_duration.time()
def run_pipeline():
    logger.info("Pipeline a commencé")
    pipeline_status.set(0)  # En cours

    engine = create_engine(get_source_db_url())
    query = "SELECT * FROM customers"

    total_extracted = 0
    total_transformed = 0
    total_loaded = 0

    for chunk in pd.read_sql(query, engine, chunksize=10000):
        logger.info(f"Processing chunk: {len(chunk)} rows")
        total_extracted += len(chunk)

        # Transformation
        chunk = retry(lambda: transform(chunk))
        total_transformed += len(chunk)

        # Chargement
        retry(lambda: load(chunk))
        total_loaded += len(chunk)

    rows_extracted.inc(total_extracted)
    rows_transformed.inc(total_transformed)
    rows_loaded.inc(total_loaded)
    data_size.set(total_loaded)
    pipeline_status.set(1)

    logger.info("Le Pipeline a terminé avec succès")

if __name__ == "__main__":
    while True:
        try:
            run_pipeline()
            time.sleep(60)  # run every minute
        except Exception as e:
            pipeline_status.set(0)
            logger.critical(f"Le Pipeline a échoué: {e}")
            time.sleep(30)
