import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def load(df, engine=None):
    if engine is None:
        from scripts.config_loader import get_target_db_url
        from sqlalchemy import create_engine
        engine = create_engine(get_target_db_url())

    df.to_sql(
        "customers",
        engine,
        if_exists="append",   # safe
        index=False,
        chunksize=10000,      # volumétrie
        method="multi"        # perf
    )

    print("Données chargées")
