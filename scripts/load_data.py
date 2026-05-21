from dotenv import load_dotenv

load_dotenv()


def load(df, engine=None):
    if engine is None:
        from sqlalchemy import create_engine

        from scripts.config_loader import get_target_db_url

        engine = create_engine(get_target_db_url())

    df.to_sql(
        "customers",
        engine,
        if_exists="append",  # safe
        index=False,
        chunksize=10000,  # volumétrie
        method="multi",  # perf
    )

    print("Données chargées")
