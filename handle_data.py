#%%
import pandas as pd
import os
import re
import json
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