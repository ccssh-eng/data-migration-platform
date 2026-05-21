import pandas as pd

df = pd.read_csv("data_raw/customers_legacy.csv")

# supprimer doublons
df = df.drop_duplicates()

# supprimer lignes sans nom
df = df.dropna(subset=["name"])

# nettoyer emails
df["email"] = df["email"].str.lower()
df = df[df["email"].str.contains("@")]

# corriger dates
df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

# supprimer dates invalides
df = df.dropna(subset=["signup_date"])

# normaliser pays
df["country"] = df["country"].replace({"France": "FR"})

df.to_csv("data_clean/customers_clean.csv", index=False)

print("Données nettoyées")
