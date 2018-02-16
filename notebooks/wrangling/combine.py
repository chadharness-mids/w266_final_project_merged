
import pandas as pd
import os

mypath = '/home/robmulla/Documents/W266/w266_final_project/notebooks/Scrape_All_Game_Threads/data'
onlyfiles = [f for f in os.listdir(mypath) if f.endswith('pickle')]

# combined_df = pd.DataFrame()

dfs = []

for file in onlyfiles:
    df = pd.read_pickle(mypath+'/'+file)
    print(file)
    print(df.shape)
    # combined_df = combined_df.append(df)
    dfs.append(df)
combined_df = pd.concat(dfs, ignore_index=True)
print(combined_df.shape)
combined_db.to_pickle('Combined.pickle')
