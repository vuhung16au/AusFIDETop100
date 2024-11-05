import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

import requests
import openpyxl

# Need to install fide-ratings-scraper on your local machine
# https://github.com/xRuiAlves/fide-ratings-scraper
# Function to fetch ELO data from the API
def fetch_elo_data(fide_id):
    """ 
    Fetch ELO data from the API
    :param fide_id: FIDE ID of the player
    :return: Dictionary containing standard, rapid, and blitz ELO ratings
    """
    url = f"http://localhost:3000/player/{fide_id}/elo"
    response = requests.get(url)
    if response.status_code == 200:
        #return response.json()
        data = response.json()
        return {
            "standard_elo": data.get("standard_elo", None),
            "rapid_elo": data.get("rapid_elo", None),
            "blitz_elo": data.get("blitz_elo", None)
        }
    else:
        raise Exception(f"Failed to fetch data for FIDE ID {fide_id}")

# List to store player data
players = []

# Use headless mode to avoid opening a browser window
options = webdriver.ChromeOptions()
options.headless = True
driver = webdriver.Chrome(options=options)

# Open the webpage Aus Top 100 FIDE Rated Players
driver.get("https://ratings.fide.com/topfed.phtml?ina=1&country=AUS")

# Find the total number of rows in the table
rows = driver.find_elements(By.XPATH, "//div[@id='main-col']//table[@cellspacing='0']//tr")
total = len(rows)

# Loop through the rows and collect names
for row in range(2, total + 1):  # Starting from row 2 as in Java code
    rank = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[1]").text
    name = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[2]").text
    
    # Sample data: <a href=card.phtml?event=4300033 class=tur>&nbsp;Cheng, Bobby</a> 
    # extract the FIDE ID from the href attribute
    fide_id = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[2]/a").get_attribute("href")
    fide_id = fide_id.split("=")[-1]  # Extract the FIDE ID from the URL
    
    name = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[2]").text
    title = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[3]").text
    fed = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[4]").text
    rating = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[5]").text
    G = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[6]").text
    title = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[3]").text
    fed = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[4]").text
    rating = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[5]").text
    G = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[6]").text
    byear = driver.find_element(By.XPATH, f"//div[@id='main-col']//table[@cellspacing='0']//tr[{row}]/td[7]").text


    player = {
        "rank": rank,
        "name": name,
        "fide_id": fide_id,
        "title": title,
        "fed": fed,
        "rating": rating,
        "G": G,
        "byear": byear
    }
    players.append(player)

driver.quit()

for player in players:
    print(f"{player['rank']}, \"{player['name']}\", {player['fide_id']}, {player['title']}, {player['fed']}, {player['rating']}, {player['G']}, {player['byear']}")

# players' rapid and blitz ratings are not available in the table
# we can fetch them from the FIDE API using the FIDE ID
for player in players:
    elo_data = fetch_elo_data(player["fide_id"])
    player["standard_elo"] = elo_data["standard_elo"]
    player["rapid_elo"] = elo_data["rapid_elo"]
    player["blitz_elo"] = elo_data["blitz_elo"]

    print(f"{player['rank']}, \"{player['name']}\", {player['fide_id']}, {player['title']}, {player['fed']}, {player['rating']}, {player['G']}, {player['byear']}, {player['standard_elo']}, {player['rapid_elo']}, {player['blitz_elo']}")

df = pd.DataFrame(players)
# Remove the "rating" column (duplicate of "standard_elo")
df = df.drop(columns=["rating"])
# Remove the FED column (All of them are AUS)
df = df.drop(columns=["fed"])

# Save the data to an Excel file
df.to_excel(f"AusTop100-{datetime.now().strftime('%Y-%m-%d')}.xlsx", index=False)

