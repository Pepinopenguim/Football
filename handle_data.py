#%%
import pandas as pd
import os
import re
import json

def as_html(df):
    with open("view.html", "w") as f:
        f.write(df.to_html())
#%%
df = pd.DataFrame()

for csv in os.listdir("data"):
    new_data = pd.read_csv(f"data\\{csv}")
    clubname = csv.replace(".csv", "")

    new_data["clubname"] = clubname

    df = pd.concat((df, new_data))



#%% ===== Get all Pos ====
pos_mapper = {pos:[1,1,1] for pos in df["Pos"].unique()}
pos_mapper    

#%% ===== Treat birthdays for just year =====
def get_year(strg):
    pattern = r"(\d{4})"

    m = re.search(pattern, strg)
    if m:
        year= m.group()
        return int(year)
    return False

df["Birthday"] = [get_year(i) for i in df["Birthday"]]

df

#%% ===== convert value to numeric =====

def get_value(strg):
    from random import randint
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
    return randint(1, 100)


df["value_1k"] = [get_value(i) for i in df["value"]]
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

if False:
    for clubname in os.listdir("data"):
        clubname = clubname.split(".")[0]
        print(clubname)
        a = int(input())
        mapper[clubname] = cs[a]

# %%
mapper = {'Botafogo de Futebol e Regatas': 'botafogo de futebol e regatas.svg',
 'Ceará Sporting Club': 'ceará sporting club.svg',
 'Clube Atlético Mineiro': 'Atlético-MG.svg',
 'Clube de Regatas Vasco da Gama': 'Vasco.svg',
 'CR Flamengo': 'Flamengo.svg',
 'Cruzeiro Esporte Clube': 'Cruzeiro.svg',
 'Esporte Clube Bahia': 'Bahia.svg',
 'Esporte Clube Juventude': 'Juventude.svg',
 'Esporte Clube Vitória': 'Vitória.svg',
 'Fluminense Football Club': 'Fluminense.svg',
 'Fortaleza Esporte Clube': 'Fortaleza.svg',
 'Grêmio Foot-Ball Porto Alegrense': 'Grêmio.svg',
 'Mirassol Futebol Clube (SP)': 'Mirassol.svg',
 'Red Bull Bragantino': 'Bragantino.svg',
 'Santos FC': 'Santos.svg',
 'Sociedade Esportiva Palmeiras': 'Palmeiras.svg',
 'Sport Club Corinthians Paulista': 'Corinthians.svg',
 'Sport Club do Recife': 'Sport.svg',
 'Sport Club Internacional': 'Internacional.svg',
 'São Paulo Futebol Clube': 'São Paulo.svg'}

# %%
# Define a formula for the quality of a player
def evaluate_player(age:int, value:int, position:str):
    # define max_value
    MIN_VALUE, MAX_VALUE = 1, 200000# in 1k euro

    def age_multipliter(age):
        # experience should make the stats
        # slightly bigger
        if age <= 17:
            return .7
        elif age <= 23:
            return .7 + ((age - 18)/(23-18)) * .3
        elif age <= 40:
            return 1 + ((age - 23)/(40-23)) * .3
        else:
            return 1.3
    
    norm_value = age_multipliter(age) * value
    
    def value_to_stat(value):
        from numpy import log as ln
        # log function where
        # if
        # value = 1k -> 30
        # value = 200m -> 100
        return int(5.734850351364555 * ln(value) + 30)

    base_stat = value_to_stat(norm_value)

    pos_mapper = {
        'Goalkeeper': [5, 10, 85],
        'Centre-Back': [10, 20, 70],
        'Left-Back': [15, 25, 60],
        'Right-Back':[15, 25, 60],
        'Defensive Midfield': [20, 20, 40],
        'Central Midfield': [30, 40, 30],
        'Attacking Midfield': [45, 35, 20],
        'Left Winger': [60, 30, 10],
        'Right Winger': [60, 30, 10],
        'Second Striker': [65, 30, 5],
        'Centre-Forward': [70, 25, 5],
        'Striker': [75, 20, 5]
    }

    stats = []
    for mult in pos_mapper[position]:
        mult = (mult) / 100

        s = (.4 * base_stat + .6 * mult * base_stat )
        s = round(s)
        stats.append(s)
    
    return base_stat, *stats

from datetime import datetime

cur_year = datetime.now().year
print(df.columns)
df[["base_stat", "atk", "mid", "dfs"]] = df.apply(
    lambda row: pd.Series(
        evaluate_player(
            age = cur_year - row["Birthday"],
            value=row["value_1k"],
            position=row["Pos"]
        )
    ),
    axis=1
)
df.head(len(df))
# %% Sorting by value
as_html(df.groupby("clubname")[["value_1k"]].sum().sort_values("value_1k", ascending=False))

# %% Sorting by stats
basestat_df = df.groupby(["clubname", "Pos"])[["base_stat"]].mean()
as_html(basestat_df)