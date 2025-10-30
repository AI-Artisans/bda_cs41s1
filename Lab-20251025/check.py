import pandas as pd
df = pd.read_csv('20251025 - dataset - Wk12.csv')
print('Dataset shape:', df.shape); print('\nColumn names:')
print(df.columns.tolist())
print('\nData types:')
print(df.dtypes); 
print('\nMissing values:')
print(df.isnull().sum())