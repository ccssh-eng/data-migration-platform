import pandas as pd

from scripts.extract import extract


def test_extract_returns_dataframe():
    df = extract()
    assert isinstance(df, pd.DataFrame), "Extract devrait retourner un DataFrame"
    assert not df.empty, "Le DataFrame extrait ne doit pas être vide"


def test_extract_columns():
    df = extract()
    expected_columns = {"id", "name", "email", "signup_date", "country"}
    assert expected_columns.issubset(
        df.columns
    ), f"Colonnes manquantes : {expected_columns - set(df.columns)}"
