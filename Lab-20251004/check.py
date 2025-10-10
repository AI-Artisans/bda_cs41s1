import pandas as pd
df = pd.read_csv("ecommerce_customer_service_satisfaction.csv")
print(df.shape)              # records, fields  (answers 2b)
print(df.dtypes)             # names + inferred types (answers 2a)
df.head(3)
