import pandas as pd
import re
import logging

COUNTRY_MAP = {
    "FRANCE": "FR",
    "ALLEMAGNE": "DE",
    "ESPAGNE": "ES",
    "ITALIE": "IT",
    "BELGIQUE": "BE",
    "SUISSE": "CH",
    "ROYAUME-UNI": "GB",
    "UNITED KINGDOM": "GB",
    "GERMANY": "DE",
    "SPAIN": "ES",
    "ITALY": "IT",
}

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, str(email)))

def transform(df: pd.DataFrame) -> pd.DataFrame:

    logging.warning(f"TRANSFORM START — {len(df)} lignes brutes")

    # Nettoyage colonnes
    df.columns = [col.strip().lower() for col in df.columns]
    df = df.drop_duplicates()

    # name
    if "name" in df.columns:
        df["name"] = df["name"].fillna("INCONNU")
        df["name"] = df["name"].astype(str).str.strip().str.upper()
        df = df[df["name"] != "NONE"]

    # email — validation stricte
    if "email" in df.columns:
        df["email"] = df["email"].astype(str).str.strip().str.lower()
        before = len(df)
        df = df[df["email"].apply(validate_email)]
        after = len(df)
        logging.warning(f"EMAILS INVALIDES REJETÉS: {before - after}")

    # signup_date
    if "signup_date" in df.columns:
        df["signup_date"] = pd.to_datetime(
            df["signup_date"],
            errors="coerce"
        )
        df["signup_date"] = df["signup_date"].fillna(pd.Timestamp.now())

    # country — standardisation
    if "country" in df.columns:
        df["country"] = (
            df["country"]
            .fillna("UNKNOWN")
            .astype(str)
            .str.strip()
            .str.upper()
        )
        df["country"] = df["country"].replace(COUNTRY_MAP)

    logging.warning(f"TRANSFORM END — {len(df)} lignes propres")

    df.to_csv("/tmp/customers_clean.csv", index=False)

    return df

