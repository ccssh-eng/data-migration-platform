import pandas as pd
from scripts.transform import transform

def test_transform_basic():
    df = pd.DataFrame({
        "id": [1, 2, 2],
        "name": ["John", None, "Alice"],
        "email": ["a@x.com", "b@x", "c@x.com"],
        "signup_date": ["2022-01-01", "bad-date", "2022-03-01"],
        "country": ["FR", "FR", "France"]
    })
    df_clean = transform(df)
    assert df_clean.shape[0] == 1
    assert set(df_clean["country"]) == {"FR"}

def test_transform_removes_invalid_email():
    import pandas as pd
    from scripts.transform import transform

    df = pd.DataFrame({
        "name": ["A", "B"],
        "email": ["test@test.com", "invalid"],
        "signup_date": ["2020-01-01", "2020-01-01"],
        "country": ["France", "France"]
    })

    result = transform(df)

    assert len(result) == 1
