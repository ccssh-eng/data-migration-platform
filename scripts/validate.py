import pandas as pd

source = pd.read_csv("../data_raw/customers_legacy.csv")
target = pd.read_csv("../data_clean/customers_clean.csv")

print("Source rows:", len(source))
print("Target rows:", len(target))
