import pandas as pd

df = pd.read_csv('discography.csv')
print(df.shape)
df = df[~df['name'].str.contains('(Live)')]
df = df[~df['name'].str.contains('(Reprise)')]
df = df[~df['name'].str.contains('Remix')]
df = df[~df['name'].str.contains('- Live')]
df = df[~df['name'].str.contains('- Instrumental')]
df = df.sort_values(by='popularity', ascending=False)
df['release_date'] = pd.to_datetime(df['release_date'])
df = df.drop_duplicates('name', keep='first')
df.to_csv('discography_cleaned.csv', index=False)
print(df)