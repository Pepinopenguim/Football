from bs4 import BeautifulSoup
import requests
import os
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

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

def get_images():

    URL = r"https://ge.globo.com/futebol/brasileirao-serie-a/"

    soup = get_soup(URL)

    images = soup.find_all("img", class_=lambda x: x and "equipes__escudo--" in x)

    for img in images:
        if "default" not in str(img):
            src, title = img["src"], img["title"]

            extension = src.split(".")[-1]
            
            img_data = requests.get(src).content
            img_file = f"{title}.{extension}"
            img_path = f"images\\{img_file}"
            
            if img_file in os.listdir("images"):

                continue

            with open(img_path, "wb") as handler:
                handler.write(img_data)

def get_tfmkt_urls():
    URL = r"https://www.transfermarkt.com/campeonato-brasileiro-serie-a/startseite/wettbewerb/BRA1"

    soup = get_soup(URL)

    tds = soup.find_all("td", class_="hauptlink no-border-links")
    
    club_hrefs = []
    for td in tds:
        club = td.find("a")
        club_hrefs.append({
            "title" : club["title"],
            "url" : r"https://www.transfermarkt.com" + club["href"],
        })

    return club_hrefs

def get_members(club_dict:dict):

    title = club_dict["title"]
    URL = club_dict["url"]

    if f"{title}.csv" in os.listdir("data"):
        return

    print(f"> get_members:{title}")

    soup = get_soup(URL)
    

    table = soup.find("table", class_="items")


    try:
        with open(f"data\\{title}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            wanted_ind = [0, 3, 4, 5, 7]
            title_columns = ["Num", "_", "_", "Name", "Pos", "Birthday", "_", "value"]
            writer.writerow([title_columns[i] for i in wanted_ind])
            for tr in table.find_all("tr", class_=lambda x: x and "odd" == x or "even" == x):
                
                tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                writer.writerow([tds[i] for i in wanted_ind])
    except AttributeError:
        print(f">> Something happened with {title}. Continuing...")
        return

if __name__ == "__main__":
    
    if not os.path.exists("images"):
        os.mkdir("images")
    
    if not os.path.exists("data"):
        os.mkdir("data")

    get_images()

    for club in get_tfmkt_urls():
        get_members(club)
