import pandas as pd

def transform(df):
    df = df.copy()

    df = df.drop_duplicates()
    df = df.dropna(subset=["name"])

    df["email"] = df["email"].str.lower()
    df = df[df["email"].str.contains("@")]

    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df = df.dropna(subset=["signup_date"])

    df["country"] = df["country"].replace({"France": "FR"})

    return df
