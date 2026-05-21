import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:password@localhost:5432/migration_db")

df = pd.read_csv("../data_clean/customers_clean.csv")

df.to_sql("customers", engine, if_exists="replace", index=False)

print("Données chargées dans PostgreSQL")
