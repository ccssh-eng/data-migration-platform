import pandas as pd
import pytest
from src.core.transform import transform

def test_email_invalide_rejete():
    df = pd.DataFrame({
        "name": ["JOHN", "JANE"],
        "email": ["john@email.com", "jane@email"],  # jane invalide
        "signup_date": ["2022-01-01", None],
        "country": ["FR", "FRANCE"]
    })
    result = transform(df)
    assert len(result) == 1
    assert result.iloc[0]["email"] == "john@email.com"

def test_country_standardise():
    df = pd.DataFrame({
        "name": ["JOHN"],
        "email": ["john@email.com"],
        "signup_date": ["2022-01-01"],
        "country": ["FRANCE"]
    })
    result = transform(df)
    assert result.iloc[0]["country"] == "FR"

def test_name_null_remplace():
    df = pd.DataFrame({
        "name": [None],
        "email": ["john@email.com"],
        "signup_date": ["2022-01-01"],
        "country": ["FR"]
    })
    result = transform(df)
    assert result.iloc[0]["name"] == "INCONNU"

def test_signup_date_null_remplace():
    df = pd.DataFrame({
        "name": ["JOHN"],
        "email": ["john@email.com"],
        "signup_date": [None],
        "country": ["FR"]
    })
    result = transform(df)
    assert pd.notna(result.iloc[0]["signup_date"])

