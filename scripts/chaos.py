def simulate_db_failure():
    from sqlalchemy import create_engine
    create_engine("wrong_url").connect()

def simulate_bad_data(df):
    df["signup_date"] = "INVALID"
    return df

def simulate_crash():
    raise Exception("Panne simulée")
