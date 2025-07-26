from bs4 import BeautifulSoup
import requests
import os
import re
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import unicodedata

def chkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        return False
    return True

def normalize_unicode(text, form='NFC'):
    return unicodedata.normalize(form, text)

def get_soup(URL):
    print(f"> Getting soup for {URL}")
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    driver.get(URL)
    driver.implicitly_wait(3)
    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, "html.parser")
    print("> Soup was delicious!")
    return soup

def get_tfmkt_urls(URL) -> dict:
    
    soup = get_soup(URL)

    table = soup.find("table", class_="items")

    countries = table.find_all("img", class_="flaggenrahmen")

    trs = table.find_all("tr", class_=lambda x: x and (x == "even" or x == "odd"))

    if len(trs) != len(countries):
        raise Exception("Country and league Lengths do not match")

    leagues = []
    for i, tr in enumerate(trs):
        league = tr.find("a", title=lambda x: x is not None)
        country = countries[i]["title"]
        title = league["title"]

        href = league["href"]
        url = r"https://www.transfermarkt.com" + href

        leagues.append({
            "title":country + " - " + title, # all because of f##ing 'bundesliga'
            "url":url
        })
    
    print(f"> {len(leagues)} urls found!")
    
    return leagues

def get_club_tfmkt_urls(league_dict) -> dict:
    league_title, URL = league_dict.values()

    soup = get_soup(URL)

    tds = soup.find_all("td", class_="hauptlink no-border-links")
    
    club_hrefs = []
    for td in tds:
        club = td.find("a")
        club_hrefs.append({
            "league title": league_title,
            "title" : club["title"],
            "url" : r"https://www.transfermarkt.com" + club["href"],
        })

    return club_hrefs

def get_members(club_dict:dict, folder, try_again:int=10):
    folder = normalize_unicode(folder)
    league_title, clubname, URL = (normalize_unicode(i) for i in club_dict.values())

    data_path = f"{folder}//data//{league_title}"
    csvfile_name = f"{clubname}.csv"
        
    if not chkdir(data_path):
        pass
    elif csvfile_name in os.listdir(data_path):
        return

    print(f"> get_members:{clubname}")

    soup = get_soup(URL)
    

    table = soup.find("table", class_="items")

    try:
        get_image(soup, league_title, clubname, folder)
    except Exception as e:
        print(">> Get image failed, trying again!")
        print(f">> Exception {e}")

        if try_again > 0:
            get_members(club_dict, folder, try_again - 1)

    try:
        with open(os.path.join(data_path, csvfile_name), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            wanted_ind = [0, 3, 4, 5, 7]
            title_columns = ["Num", "_", "_", "Name", "Pos", "Birthday", "_", "value"]
            writer.writerow([title_columns[i] for i in wanted_ind])
            for tr in table.find_all("tr", class_=lambda x: x and "odd" == x or "even" == x):
                
                tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                writer.writerow([tds[i] for i in wanted_ind])
    except AttributeError:
        print(f">> Something happened with {clubname}.")
        if csvfile_name in os.listdir(data_path):
            print(">> deleting file!")
            os.remove(
                os.path.join(data_path, csvfile_name)
            )
        if try_again:
            print(">> Trying again!")
            get_members(club_dict, folder, try_again - 1)
        else:
            print(f">> All tries failed! Continuing")
        return

RUN = "EU"

def get_image(club_soup, league_title, clubname, folder):

    img_file = f"{clubname}.png"
    img_path = f"{folder}//images//{league_title}//{img_file}"

    chkdir(f"{folder}//images//{league_title}")

    if img_file in os.listdir(f"{folder}//images//"):
        return

    div = club_soup.find("div", class_=lambda x: x and "profile-container" in x)
    if div:
        img = div.find("img")
    else:
        raise Exception("ImageFileNotFound!")

    src, title = img["src"], normalize_unicode(img["title"])


    img_data = requests.get(src).content

    with open(img_path, "wb") as handler:
        print(f"> Saving {clubname}.png")
        handler.write(img_data)


if __name__ == "__main__":
    if RUN == "BR":
        chkdir("images")
        
        chkdir("data")

        get_images(r"https://ge.globo.com/futebol/brasileirao-serie-a/")

        for club in get_club_tfmkt_urls(r"https://www.transfermarkt.com/campeonato-brasileiro-serie-a/startseite/wettbewerb/BRA1"):
            get_members(club)

    elif RUN == "EU":
        
        chkdir(RUN)
        chkdir(f"{RUN}//data")
        chkdir(f"{RUN}//images")


        leagues = get_tfmkt_urls(r"https://www.transfermarkt.com/wettbewerbe/europa")

        for league in leagues:
            clubs = get_club_tfmkt_urls(league)

            for club in clubs:
                get_members(club, RUN)


            
        
