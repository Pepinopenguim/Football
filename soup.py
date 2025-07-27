from bs4 import BeautifulSoup
import requests
import os
import re
import json
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import unicodedata
import time
from handle_data import handle_csv

class ServersUnavailable(Exception):
    pass

def chkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        return False
    return True

def normalize_unicode(text, form='NFC'):
    return unicodedata.normalize(form, text)

class Tfmkt:
    def __init__(self, mode):
        self.mode = mode.upper()
        self.setup_driver()

        match self.mode:
            case "EU":
                self.league_json = f"{self.mode}//base.json"

                chkdir(self.mode)
                chkdir(f"{self.mode}//data")
                chkdir(f"{self.mode}//images")


                if os.path.basename(self.league_json) in os.listdir(self.mode):
                    self.leagues = json.load(
                        open(self.league_json, "r", encoding="utf-8")
                    )
                else:
                    self.leagues = self.get_tfmkt_leagues(r"https://www.transfermarkt.com/wettbewerbe/europa")

                self.loop_through_leagues()

            case "GETLEAGUESMANUAL":
                self.get_leagues_manually()
    
    def get_leagues_manually(self):

        self.driver.get(r"https://www.transfermarkt.com/wettbewerbe/europa")

        ask = input("> aperte enter para salvar page source.")

        soups = []
        while "q" not in ask.lower():
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            soups.append(soup)
            ask = input("> aperte enter para salvar page source.")
        
        league_dicts = []
        for soup in soups:
            
            table = soup.find("table", class_="items")
        
            trs = table.find_all("tr", class_=lambda x: x and (x == "even" or x == "odd"))
            
            for i, tr in enumerate(trs):
                country = tr.find("img", class_="flaggenrahmen")["title"]

                league = tr.find("a", title=lambda x: x is not None)
                title = league["title"]
                href = league["href"]
                url = r"https://www.transfermarkt.com" + href

                league_dicts.append({
                    "country":country,
                    "title": title, 
                    "url":url,
                    "saved":False,
                })
        mode = input("insert mode: ")
        with open(f"{mode}//base.json", "w", encoding="utf-8") as j:
            json.dump(league_dicts, j, indent=4)
        
        exit(0)

    
    def loop_through_leagues(self):
        for league in self.leagues:
                if league["saved"]:
                    print(f"> {league["title"]} already saved")
                    continue

                
                self.clubs = self.get_club_tfmkt_urls(league)
                while len(self.clubs) == 0:
                    self.clubs = self.get_club_tfmkt_urls(league)
                    
                for club in self.clubs:
                    self.get_members(club, self.mode)

                # Set as saved
                self.update_json(
                    path_to_json=self.league_json,
                    dict_={
                        "country":league["country"],
                        "title":league["title"]
                    }
                )

    def update_json(self, path_to_json, dict_, save_key = "saved"):
        with open(path_to_json, "r", encoding="utf-8") as f:
            base = json.load(f)

        for d in base:  
            mask = True
            for key, value in dict_.items():
                mask = key in d and value == d[key] and mask
            if mask:
                d[save_key] = mask
                break

        with open(path_to_json, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=4)

    def setup_driver(self):
        options = Options()
        #options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(3)

        self.driver.get("about:blank")

    def get_soup(self, URL):
        print(f"> Getting soup for {URL}")
        
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(URL)
        time.sleep(.5)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        print("> Soup was delicious!")
        return soup

    def get_tfmkt_leagues(self, URL) -> dict:
        
        soup = self.get_soup(URL)

        h1 = club_soup.find("h1", string="503 Service Unavailable")
        if h1 is not None:
            raise ServersUnavailable()

        table = soup.find("table", class_="items")
        
        trs = table.find_all("tr", class_=lambda x: x and (x == "even" or x == "odd"))
        
        leagues = []
        for i, tr in enumerate(trs):
            country = tr.find("img", class_="flaggenrahmen")["title"]

            league = tr.find("a", title=lambda x: x is not None)
            title = league["title"]
            href = league["href"]
            url = r"https://www.transfermarkt.com" + href

            leagues.append({
                "country":country,
                "title": title, 
                "url":url,
                "saved":False,
            })
            
        print(f"> {len(leagues)} urls found!")
        
        with open(self.league_json, "w", encoding="utf-8") as j:
            json.dump(leagues, j)

        return leagues

    def get_club_tfmkt_urls(self, league_dict) -> dict:
        country, league_title, URL, is_saved = league_dict.values()

        chkdir(f"{self.mode}//data//{country}")
        chkdir(f"{self.mode}//data//{country}//{league_title}")

        path_to_league = f"{self.mode}//data//{country}//{league_title}"

        if "base.json" in os.listdir(path_to_league):
            with open(os.path.join(path_to_league, "base.json"), "r", encoding="utf-8") as fp:
                return json.load(fp)

        soup = self.get_soup(URL)


        tds = soup.find_all("td", class_="hauptlink no-border-links")

        club_hrefs = []
        for td in tds:
            club = td.find("a")
            clubname = club["title"]
            club_hrefs.append({
                "country": country,
                "league title": league_title,
                "title" : clubname,
                "url" : r"https://www.transfermarkt.com" + club["href"],
                "saved" : f"{clubname}.csv" in os.listdir(path_to_league)
            })

        json_path = os.path.join(path_to_league, "base.json")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(club_hrefs, f, indent=4)
            f.close()



        return club_hrefs

    def get_members(self, club_dict:dict, folder, try_again:int=10):
        country, league_title, clubname, URL, is_saved = club_dict.values()

        data_path = rf"{folder}\data\{country}\{league_title}"
        csvfile_name = f"{clubname}.csv"

        
        if is_saved:
            return

        print(f"> get_members:{clubname}")

        soup = self.get_soup(URL)

        table = soup.find("table", class_="items")

        try:
            self.get_image(soup, country, league_title, clubname, folder)
        except ServersUnavailable:
            print(">> Servers are offline, waiting...")
            time.sleep(10)
            self.get_members(club_dict, folder, try_again)
        except Exception as e:
            print(">> Get image failed, trying again!")
            print(f">> Exception {e}")

            if try_again > 0:
                self.get_members(club_dict, folder, try_again - 1)

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
                self.get_members(club_dict, folder, try_again - 1)
            else:
                print(f">> All tries failed! Continuing")
            return
        
        handle_csv(os.path.join(data_path, csvfile_name))

        # save information
        self.update_json(
            path_to_json=f"{self.mode}//data//{country}//{league_title}//base.json",
            dict_={
                "country":country,
                "league title":league_title,
                "title":clubname
            }
        )


    def get_image(self, club_soup, country, league_title, clubname, folder):

        img_file = f"{clubname}.png"
        img_path = f"{folder}//images//{country}//{league_title}"
        img_file_path = os.path.join(img_path, img_file)

        chkdir(os.path.dirname(img_path))
        chkdir(img_path)

        if img_file in img_path:
            return

        # check if servers are available
        h1 = club_soup.find("h1", string="503 Service Unavailable")
        if h1 is not None:
            raise ServersUnavailable()

        div = club_soup.find("div", class_=lambda x: x and "profile-container" in x)

        if div:
            img = div.find("img")
        else:
            raise Exception("ImageFileNotFound!")

        src, title = img["src"], normalize_unicode(img["title"])

        img_data = requests.get(src).content

        with open(img_file_path, "wb") as handler:
            print(f"> Saving {clubname}.png")
            handler.write(img_data)

if __name__ == "__main__":
    tfmkt = Tfmkt(mode="EU")
