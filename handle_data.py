#%%
import pandas as pd
import os as os
import re

#%%
df = pd.DataFrame()

for csv in os.listdir("data"):
    new_data = pd.read_csv(f"data\\{csv}")
    clubname = csv.replace(".csv", "")

    new_data["clubname"] = clubname

    df = pd.concat((df, new_data))



#%% ===== Get all Pos ====
df["Pos"].unique()

#%% ===== Treat birthdays for just year =====
def get_year(strg):
    pattern = r"(\d{4})"

    m = re.search(pattern, strg)
    if m:
        year= m.group()
        return year
    return False

df["Birthday"] = [get_year(i) for i in df["Birthday"]]

df

#%% ===== convert value to numeric =====

def get_value(strg):
    pattern = r"€([\d.,]+)([mk])"

    m = re.search(pattern, strg, re.IGNORECASE)
    if m:
        value, suffix = m.groups()

        value.replace(",", ".")
        
        if "m" in suffix:
            value = float(value) * 1e3
        elif "k" in suffix:
            value = float(value) 
        print(value)
        return value
    return False


df["value (€1k)"] = [get_value(i) for i in df["value"]]
df = df[[i for i in df.columns if i != "value"]]
df.head(50)
#%% ===== rename svg files =====

mapper = {}

i = 0
cs = []
for k in os.listdir("images"):
    print(f"{i} - {k}")
    cs.append(k)
    i += 1

for clubname in os.listdir("data"):
    clubname = clubname.split(".")[0]
    print(clubname)
    a = int(input())
    mapper[clubname] = cs[a]



# %%
