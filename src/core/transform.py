import pandas as pd


def transform(df: pd.DataFrame):

    df.columns = [col.strip().lower() for col in df.columns]

    df = df.drop_duplicates()

    df = df[df["email"].notna()]


    if "name" in df.columns:
        df["name"] = df["name"].astype(str).str.upper()

    if "email" in df.columns:
        df = df[df["email"].notna()]
        df = df[df["email"].str.contains("@", na=False)]
        df["email"] = df["email"].astype(str).str.lower()

    if "signup_date" in df.columns:
        df["signup_date"] = pd.to_datetime(
            df["signup_date"],
            errors="coerce"
        )

    if "country" in df.columns:
        df["country"] = (
            df["country"]
            .fillna("UNKNOWN")
            .astype(str)
            .str.upper()
        )

    df.to_csv(
        "/tmp/customers_clean.csv",
        index=False
    )

    return df

