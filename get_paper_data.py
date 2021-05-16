import pandas as pd 

table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
df = table[0]
df.to_csv('paper_data/S&P500-Info.csv')
df.to_csv("paper_data/S&P500-Symbols.csv", columns=['Symbol'])