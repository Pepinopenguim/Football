
import pandas as pd
import os
import re
from datetime import datetime
from random import randint
from numpy import log as ln


def as_html(df):
    with open("view.html", "w", encoding="utf-8") as f:
        f.write(df.to_html())

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
    
    value_to_stat = lambda x: int(5.33 * ln(x) + 30)

    # def value_to_stat(value):
    #     from numpy import log as ln
    #     # log function where
    #     # if
    #     # value = 1k -> 30
    #     # value = 200m -> 100
    #     return int(5.734850351364555 * ln(value) + 30)

    base_stat = value_to_stat(norm_value)

    pos_mapper = {
        'Goalkeeper': [5, 10, 85],
        'Centre-Back': [10, 20, 70],
        'Defender': [10, 20, 70],
        'Left-Back': [15, 25, 60],
        'Right-Back':[15, 25, 60],
        'Defensive Midfield': [20, 20, 40],
        'Right Midfield': [30, 40, 30],
        'Left Midfield': [30, 40, 30],
        'Midfielder': [30, 40, 30],
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

def treat_year(strg):
    pattern = r"(\d{4})"

    m = re.search(pattern, strg)
    if m:
        year= m.group()
        return int(year)
    return False

def treat_value(strg):
    pattern = r"€([\d.,]+)([mk])"

    m = re.search(pattern, strg, re.IGNORECASE)
    if m:
        value, suffix = m.groups()

        value.replace(",", ".")
        
        if "m" in suffix:
            value = float(value) * 1e3
        elif "k" in suffix:
            value = float(value) 
        return value
    return randint(1, 100)

def handle_csv(path_to_csv:str):

    # convert to dataframe
    df = pd.read_csv(path_to_csv)
    df.columns = [c.lower() for c in df.columns]

    # get league and clubname
    pattern = r"data\\(.*) - (.*)\\(.*).csv"
    m = re.search(pattern, path_to_csv)
    if m is None:
        return pd.DataFrame()
    country, league_title, clubname = m.groups()

    df["country"] = country
    df["league"] = league_title
    df["clubname"] = clubname

    new_cols = ["country", "league", "clubname"]

    df = df[new_cols + [i for i in df.columns if i not in new_cols]]

    if "atk" in df.columns:
        # is treated!
        print(f">> {path_to_csv} is treated")
        return df

    # treat birthday
    df["birthyear"] = [treat_year(i) for i in df["birthday"]]

    # treat value
    
    if "value_1k" not in df.columns:
        df["value_1k"] = [treat_value(i) for i in df["value"]]
    
    cur_year = datetime.now().year

    df[["base_stat", "atk", "mid", "dfs"]] = df.apply(
        lambda row: pd.Series(
            evaluate_player(
                age = cur_year - row["birthyear"],
                value=row["value_1k"],
                position=row["pos"]
            )
        ),
        axis=1
    )
    print(f"> Saving {path_to_csv}")
    df.to_csv(path_to_csv, index=False)

    return df


def walk_through_csvs(dir):

    dfs = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            path_to_file = os.path.join(root, file)
            if file.lower().endswith(".csv"):
                dfs.append(handle_csv(path_to_file))

    df = pd.concat(dfs)

    df.to_csv(os.path.join(dir, "data.csv"), index=False)

    as_html(df)

                


walk_through_csvs(r"EU\data")