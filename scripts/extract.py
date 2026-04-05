from sqlalchemy import create_engine
import pandas as pd
from scripts.config_loader import get_source_db_url

def extract():
    engine = create_engine(get_source_db_url())
    query = "SELECT * FROM customers"
    df = pd.read_sql(query, engine)
    return df
