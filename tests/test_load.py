def test_load():
    import pandas as pd
    from sqlalchemy import create_engine

    from scripts.load_data import load

    engine = create_engine("sqlite:///:memory:")

    df = pd.DataFrame(
        {
            "id": [1],
            "name": ["test"],
            "email": ["a@test.com"],
            "signup_date": ["2020-01-01"],
            "country": ["FR"],
        }
    )

    load(df, engine)

    result = pd.read_sql("customers", engine)
    assert len(result) == 1
